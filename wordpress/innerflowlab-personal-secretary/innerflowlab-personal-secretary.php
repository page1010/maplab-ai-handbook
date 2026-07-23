<?php
/**
 * Plugin Name: InnerFlowLab Personal Secretary
 * Description: Private, read-only MAPLAB and Investment OS operations summary for the site owner.
 * Version: 0.3.0
 * Author: InnerFlowLab
 * Requires at least: 6.5
 * Requires PHP: 8.0
 */

if (!defined('ABSPATH')) {
    exit;
}

final class IFL_Personal_Secretary {
    private const OPTION_KEY = 'ifl_personal_secretary_snapshot';
    private const PAGE_SLUG = 'personal-secretary';
    private const REST_NAMESPACE = 'innerflowlab-secretary/v1';
    private const MAX_SNAPSHOT_BYTES = 131072;

    public static function boot(): void {
        add_action('init', [self::class, 'register_shortcodes']);
        add_action('rest_api_init', [self::class, 'register_rest_routes']);
        add_action('template_redirect', [self::class, 'guard_secretary_page']);
        add_action('send_headers', [self::class, 'send_private_headers']);
        add_filter('wp_robots', [self::class, 'noindex_secretary_page']);
    }

    public static function activate(): void {
        $existing = get_page_by_path(self::PAGE_SLUG, OBJECT, 'page');
        if ($existing instanceof WP_Post) {
            return;
        }

        wp_insert_post([
            'post_title' => '個人秘書',
            'post_name' => self::PAGE_SLUG,
            'post_status' => 'publish',
            'post_type' => 'page',
            'post_content' => '<!-- wp:shortcode -->[innerflowlab_personal_secretary]<!-- /wp:shortcode -->',
            'comment_status' => 'closed',
            'ping_status' => 'closed',
        ]);
    }

    public static function register_shortcodes(): void {
        add_shortcode('innerflowlab_personal_secretary', [self::class, 'render']);
    }

    public static function register_rest_routes(): void {
        register_rest_route(self::REST_NAMESPACE, '/snapshot', [
            [
                'methods' => WP_REST_Server::READABLE,
                'callback' => [self::class, 'get_snapshot'],
                'permission_callback' => [self::class, 'can_manage'],
            ],
            [
                'methods' => WP_REST_Server::CREATABLE,
                'callback' => [self::class, 'update_snapshot'],
                'permission_callback' => [self::class, 'can_manage'],
            ],
        ]);
    }

    public static function can_manage(): bool {
        return current_user_can('manage_options');
    }

    public static function get_snapshot(): WP_REST_Response {
        return self::private_response(self::snapshot(), 200);
    }

    public static function update_snapshot(WP_REST_Request $request) {
        $body = $request->get_body();
        if (strlen($body) > self::MAX_SNAPSHOT_BYTES) {
            return new WP_Error(
                'ifl_snapshot_too_large',
                'Snapshot exceeds 128 KiB.',
                ['status' => 413]
            );
        }

        $payload = $request->get_json_params();
        if (!is_array($payload)) {
            return new WP_Error(
                'ifl_snapshot_invalid_json',
                'Snapshot must be a JSON object.',
                ['status' => 400]
            );
        }

        $validation = self::validate_snapshot($payload);
        if (is_wp_error($validation)) {
            return $validation;
        }

        $snapshot = self::sanitize_snapshot($payload);
        update_option(self::OPTION_KEY, $snapshot, false);

        return self::private_response([
            'ok' => true,
            'generated_at' => $snapshot['generated_at'],
            'roles' => count($snapshot['roles']),
            'modules' => count($snapshot['modules']),
            'dashboard_jobs' => count($snapshot['dashboard']['jobs'] ?? []),
            'market_indicators' => count($snapshot['dashboard']['market_indicators'] ?? []),
        ], 200);
    }

    public static function guard_secretary_page(): void {
        if (!is_page(self::PAGE_SLUG)) {
            return;
        }
        if (!is_user_logged_in()) {
            auth_redirect();
        }
        if (!current_user_can('manage_options')) {
            wp_die(
                esc_html__('這個私人入口只開放給網站管理員。', 'ifl-secretary'),
                esc_html__('沒有權限', 'ifl-secretary'),
                ['response' => 403]
            );
        }
    }

    public static function noindex_secretary_page(array $robots): array {
        if (is_page(self::PAGE_SLUG)) {
            $robots['noindex'] = true;
            $robots['nofollow'] = true;
            $robots['noarchive'] = true;
        }
        return $robots;
    }

    public static function send_private_headers(): void {
        if (!is_page(self::PAGE_SLUG)) {
            return;
        }
        nocache_headers();
        header('Cache-Control: private, no-store, max-age=0', true);
        header('X-Robots-Tag: noindex, nofollow, noarchive', true);
        header('Referrer-Policy: same-origin', true);
    }

    public static function render(): string {
        if (!is_user_logged_in()) {
            $login_url = wp_login_url(get_permalink());
            return '<p><a class="button" href="' . esc_url($login_url) . '">登入個人秘書</a></p>';
        }
        if (!current_user_can('manage_options')) {
            return '<p>這個私人入口只開放給網站管理員。</p>';
        }

        $snapshot = self::snapshot();
        $roles = isset($snapshot['roles']) && is_array($snapshot['roles']) ? $snapshot['roles'] : [];
        $modules = isset($snapshot['modules']) && is_array($snapshot['modules']) ? $snapshot['modules'] : [];
        $alerts = isset($snapshot['alerts']) && is_array($snapshot['alerts']) ? $snapshot['alerts'] : [];
        $dashboard = isset($snapshot['dashboard']) && is_array($snapshot['dashboard']) ? $snapshot['dashboard'] : [];
        $dashboard_kpis = isset($dashboard['kpis']) && is_array($dashboard['kpis']) ? $dashboard['kpis'] : [];
        $dashboard_market = isset($dashboard['market_indicators']) && is_array($dashboard['market_indicators']) ? $dashboard['market_indicators'] : [];
        $dashboard_products = isset($dashboard['products']) && is_array($dashboard['products']) ? $dashboard['products'] : [];
        $dashboard_jobs = isset($dashboard['jobs']) && is_array($dashboard['jobs']) ? $dashboard['jobs'] : [];
        $job_categories = ['總經風控', '阿爾法雷達', '研究證據', '交易劇本', '系統運維'];
        $jobs_by_category = array_fill_keys($job_categories, []);
        foreach ($dashboard_jobs as $job) {
            $category = isset($job['category']) ? (string) $job['category'] : '系統運維';
            if (!array_key_exists($category, $jobs_by_category)) {
                $category = '系統運維';
            }
            $jobs_by_category[$category][] = $job;
        }
        $category_descriptions = [
            '總經風控' => '市場天候、晨報、重大事件與黑天鵝。',
            '阿爾法雷達' => '跨源共振、網紅情報與海外動能。',
            '研究證據' => '籌碼、制度事件、研究圓桌與摘要。',
            '交易劇本' => '故事驗證、股期研究與開盤劇本。',
            '系統運維' => '只讀快照、新鮮度守門與 fail-closed。',
        ];
        $warning_job_count = count(array_filter(
            $dashboard_jobs,
            static fn(array $job): bool => self::status_class((string) ($job['status'] ?? 'unknown')) !== 'ok'
        ));

        ob_start();
        ?>
        <style>
            .wp-block-post-title{display:none!important}.wp-block-post-content{margin-top:0!important}
            .ifl-secretary{--night:#111d29;--night-2:#182a3b;--teal:#22c5a3;--teal-dark:#087f6b;--ink:#162536;--muted:#667587;--line:#dbe3e8;--paper:#fff;--wash:#f4f7f8;--ok:#087f61;--warn:#b76b00;--bad:#bd2c2c;max-width:1280px;margin:-92px auto 40px;padding:0 18px;color:var(--ink);font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;scroll-behavior:smooth}
            .ifl-secretary *{box-sizing:border-box}.ifl-secretary [hidden]{display:none!important}.ifl-secretary h1,.ifl-secretary h2,.ifl-secretary h3,.ifl-secretary p{max-width:none}.ifl-hero{position:relative;overflow:hidden;min-height:330px;padding:56px clamp(26px,6vw,74px);border-radius:0 0 26px 26px;background:radial-gradient(circle at 82% 18%,rgba(34,197,163,.25),transparent 27%),linear-gradient(135deg,var(--night),var(--night-2));color:#fff;box-shadow:0 22px 50px rgba(16,35,63,.16)}
            .ifl-hero:after{content:"";position:absolute;right:-75px;bottom:-145px;width:340px;height:340px;border:1px solid rgba(255,255,255,.1);border-radius:50%;box-shadow:0 0 0 45px rgba(255,255,255,.025),0 0 0 90px rgba(255,255,255,.018)}.ifl-kicker{margin:0 0 15px;font-size:12px;font-weight:750;letter-spacing:.17em;text-transform:uppercase;color:#72e0cb}.ifl-hero h1{position:relative;z-index:1;margin:0;font-size:clamp(38px,6vw,68px);line-height:1.02;letter-spacing:-.045em}.ifl-hero>p:not(.ifl-kicker){position:relative;z-index:1;max-width:790px;margin:20px 0 0;color:#cddbe6;font-size:16px;line-height:1.72}.ifl-meta{position:relative;z-index:1;display:flex;gap:9px;flex-wrap:wrap;margin-top:26px}.ifl-pill{display:inline-flex;align-items:center;padding:8px 12px;border:1px solid rgba(255,255,255,.12);border-radius:4px;background:rgba(255,255,255,.06);font-size:12px;color:#e8f1f6}
            .ifl-data-nav{position:sticky;top:18px;z-index:20;display:flex;gap:4px;overflow-x:auto;margin:18px 0 0;padding:7px;border:1px solid var(--line);border-radius:10px;background:rgba(255,255,255,.94);box-shadow:0 10px 25px rgba(15,35,52,.1);backdrop-filter:blur(12px)}.ifl-data-nav a{flex:0 0 auto;padding:10px 13px;border-radius:7px;color:#3d4f60;font-size:13px;font-weight:700;text-decoration:none}.ifl-data-nav a:hover{background:#e9f7f4;color:var(--teal-dark)}
            .ifl-section{margin-top:46px;scroll-margin-top:90px}.ifl-section-head{display:flex;justify-content:space-between;gap:22px;align-items:end;margin-bottom:17px;padding-bottom:12px;border-bottom:1px solid var(--line)}.ifl-section-head h2{margin:0;font-size:clamp(24px,3vw,34px);letter-spacing:-.025em}.ifl-section-head p{max-width:610px;margin:0;color:var(--muted);font-size:13px;line-height:1.6;text-align:right}.ifl-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:13px}
            .ifl-card{min-width:0;border:1px solid var(--line);border-top:3px solid #293e50;border-radius:4px;padding:19px;background:var(--paper);box-shadow:0 7px 22px rgba(16,35,63,.045)}.ifl-card h3{margin:9px 0 8px;font-size:17px}.ifl-card p{margin:7px 0;color:var(--muted);font-size:13px;line-height:1.6}.ifl-status{display:inline-flex;align-items:center;gap:7px;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.055em}.ifl-dot{width:8px;height:8px;border-radius:50%;background:#8796a8}.ifl-status.ok{color:var(--ok)}.ifl-status.ok .ifl-dot{background:var(--ok)}.ifl-status.warning{color:var(--warn)}.ifl-status.warning .ifl-dot{background:var(--warn)}.ifl-status.error{color:var(--bad)}.ifl-status.error .ifl-dot{background:var(--bad)}
            .ifl-verdict{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;align-items:center;padding:26px;border:1px solid #e7ca94;border-left:5px solid var(--warn);border-radius:5px;background:#fffaf0}.ifl-verdict h3{margin:7px 0 8px;font-size:clamp(23px,3vw,31px)}.ifl-verdict p{margin:0;color:var(--muted);line-height:1.6}.ifl-verdict-badge{min-width:120px;text-align:center;padding:13px 16px;border-radius:4px;background:#fff;color:var(--warn);font-size:13px;font-weight:850;box-shadow:0 5px 18px rgba(70,48,10,.08)}
            .ifl-kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:10px;margin-top:13px}.ifl-kpi{padding:16px;border:1px solid var(--line);border-radius:4px;background:#fff}.ifl-kpi small{display:block;color:var(--muted);font-size:11px;margin-bottom:7px}.ifl-kpi strong{display:block;font-size:22px;margin-bottom:7px}.ifl-kpi>span:last-child{display:block;margin-top:7px;color:var(--muted);font-size:11px;line-height:1.45}
            .ifl-market-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:11px}.ifl-indicator{position:relative;min-height:165px;padding:18px;border:1px solid var(--line);border-top:4px solid #20384b;border-radius:3px;background:#fff}.ifl-indicator h3{margin:0;color:var(--teal-dark);font-size:15px}.ifl-indicator-value{display:block;margin:17px 0 5px;font-size:28px;line-height:1;font-weight:780;letter-spacing:-.025em}.ifl-indicator-change{font-size:12px;font-weight:750;color:var(--muted)}.ifl-indicator-change.positive{color:var(--ok)}.ifl-indicator-change.negative{color:var(--bad)}.ifl-indicator footer{position:absolute;left:18px;right:18px;bottom:14px;display:flex;justify-content:space-between;gap:8px;color:#83909c;font-size:10px}
            .ifl-toolbar{display:flex;flex-wrap:wrap;gap:9px;align-items:center;margin:0 0 18px}.ifl-search{flex:1 1 270px;min-width:0;padding:11px 13px;border:1px solid #bfcbd3;border-radius:6px;background:#fff;color:var(--ink);font:inherit}.ifl-filter{padding:10px 13px;border:1px solid var(--line);border-radius:6px;background:#fff;color:#526373;font-size:12px;font-weight:750;cursor:pointer}.ifl-filter.is-active{border-color:var(--teal-dark);background:#e7f8f4;color:var(--teal-dark)}
            .ifl-category{margin-top:25px}.ifl-category-head{display:flex;justify-content:space-between;gap:14px;align-items:baseline;margin-bottom:9px}.ifl-category h3{margin:0;font-size:20px}.ifl-category-head p{margin:0;color:var(--muted);font-size:12px}.ifl-job-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:10px}.ifl-job{min-height:160px;padding:16px;border:1px solid var(--line);border-top:3px solid #2b3f4f;border-radius:3px;background:#fff}.ifl-job h4{margin:10px 0 6px;font-size:15px;line-height:1.42}.ifl-job p{margin:0;color:var(--muted);font-size:12px;line-height:1.55}.ifl-job footer{display:flex;justify-content:space-between;gap:10px;margin-top:14px;padding-top:10px;border-top:1px solid #edf1f3;color:#81909d;font-size:10px}
            .ifl-alert{border-left:4px solid var(--warn);padding:13px 16px;margin:9px 0;background:#fff9ed;border-radius:0 5px 5px 0}.ifl-alert.error{border-color:var(--bad);background:#fff3f2}.ifl-alert strong{display:block;margin-bottom:4px}.ifl-alert span{color:#5e6871;font-size:13px}.ifl-empty{padding:22px;border:1px dashed #a9b9ca;border-radius:6px;color:var(--muted);background:#f8fafb}
            .ifl-details{margin-top:12px;border:1px solid var(--line);border-radius:6px;background:#f8fafb;padding:0 16px}.ifl-details summary{cursor:pointer;padding:16px 0;font-weight:780}.ifl-details .ifl-grid{padding:3px 0 18px}.ifl-source-note{margin-top:13px;color:var(--muted);font-size:11px}.ifl-footer{margin:35px 0 10px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:11px;line-height:1.6}
            @media (max-width:760px){.ifl-secretary{margin-top:-44px;padding:0 12px}.ifl-hero{min-height:0;padding:38px 23px}.ifl-data-nav{top:8px}.ifl-section{margin-top:35px}.ifl-section-head{display:block}.ifl-section-head p{margin-top:7px;text-align:left}.ifl-verdict{grid-template-columns:1fr}.ifl-verdict-badge{text-align:left}.ifl-category-head{display:block}.ifl-category-head p{margin-top:5px}}
        </style>
        <main class="ifl-secretary">
            <section class="ifl-hero">
                <p class="ifl-kicker">InnerFlowLab · Personal Secretary</p>
                <h1>Investment OS<br>資料中心</h1>
                <p>彙整本機 18501 的總經、雷達、研究、交易與系統成果，一頁比較各作戰模組。這裡只呈現去識別化成果；帳戶、持倉、券商連線與執行權限仍安全留在 Mac。</p>
                <div class="ifl-meta">
                    <span class="ifl-pill">更新：<?php echo esc_html($snapshot['generated_at'] ?? '尚未同步'); ?></span>
                    <span class="ifl-pill">角色：<?php echo esc_html((string) count($roles)); ?></span>
                    <span class="ifl-pill">正式工作：<?php echo esc_html((string) count($dashboard_jobs)); ?></span>
                    <span class="ifl-pill">需處理：<?php echo esc_html((string) $warning_job_count); ?></span>
                    <span class="ifl-pill">安全模式：只讀鏡像</span>
                </div>
            </section>

            <nav class="ifl-data-nav" aria-label="資料中心導覽">
                <a href="#ifl-overview">總覽</a>
                <a href="#ifl-market">市場指標</a>
                <a href="#ifl-outcomes">核心成果</a>
                <a href="#ifl-workstreams">作戰模組</a>
                <a href="#ifl-alerts">警示</a>
                <a href="#ifl-roles">角色與功能</a>
            </nav>

            <section class="ifl-section" id="ifl-overview">
                <header class="ifl-section-head">
                    <h2>今日總覽</h2>
                    <p>先看整體能不能用，再看哪一條成果線需要人工處理。</p>
                </header>
                <?php if (!$dashboard): ?>
                    <div class="ifl-empty">尚未收到 18501 的去敏成果快照；現有角色與功能資料仍可在下方查看。</div>
                <?php else: ?>
                    <?php $dashboard_status = self::status_class($dashboard['status'] ?? 'unknown'); ?>
                    <div class="ifl-verdict">
                        <div>
                            <span class="ifl-status <?php echo esc_attr($dashboard_status); ?>"><i class="ifl-dot"></i><?php echo esc_html($dashboard['status'] ?? 'unknown'); ?></span>
                            <h3><?php echo esc_html($dashboard['verdict'] ?? '尚無判讀'); ?></h3>
                            <p><?php echo esc_html($dashboard['detail'] ?? ''); ?></p>
                        </div>
                        <div class="ifl-verdict-badge"><?php echo esc_html((string) $warning_job_count); ?> 項待檢查</div>
                    </div>

                    <div class="ifl-kpi-grid">
                        <?php foreach ($dashboard_kpis as $kpi): ?>
                            <?php $kpi_status = self::status_class($kpi['status'] ?? 'unknown'); ?>
                            <article class="ifl-kpi">
                                <small><?php echo esc_html($kpi['label'] ?? '指標'); ?></small>
                                <strong><?php echo esc_html($kpi['value'] ?? '未知'); ?></strong>
                                <span class="ifl-status <?php echo esc_attr($kpi_status); ?>"><i class="ifl-dot"></i><?php echo esc_html($kpi['status'] ?? 'unknown'); ?></span>
                                <span><?php echo esc_html($kpi['detail'] ?? ''); ?></span>
                            </article>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </section>

            <section class="ifl-section" id="ifl-market">
                <header class="ifl-section-head">
                    <h2>公開市場指標</h2>
                    <p>MacroMicro 式同尺寸卡片，快速橫向比較；只搬公開總經數值，不搬個股清單與投資部位。</p>
                </header>
                <?php if (!$dashboard_market): ?>
                    <div class="ifl-empty">這份快照尚未包含公開市場指標；重新同步後會出現 10Y、美元、台幣與原物料等卡片。</div>
                <?php else: ?>
                    <div class="ifl-market-grid">
                        <?php foreach ($dashboard_market as $indicator): ?>
                            <?php
                            $change = trim((string) ($indicator['change'] ?? ''));
                            $change_class = str_starts_with($change, '-') ? 'negative' : ((str_starts_with($change, '+') || (float) $change > 0) ? 'positive' : '');
                            ?>
                            <article class="ifl-indicator">
                                <h3><?php echo esc_html($indicator['name'] ?? '未命名指標'); ?></h3>
                                <strong class="ifl-indicator-value"><?php echo esc_html($indicator['value'] ?? '—'); ?></strong>
                                <span class="ifl-indicator-change <?php echo esc_attr($change_class); ?>"><?php echo esc_html($change !== '' ? $change : '變動未提供'); ?></span>
                                <footer>
                                    <span><?php echo esc_html($indicator['status'] ?? 'unknown'); ?></span>
                                    <time><?php echo esc_html($indicator['freshness'] ?? '未知'); ?></time>
                                </footer>
                            </article>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </section>

            <section class="ifl-section" id="ifl-outcomes">
                <header class="ifl-section-head">
                    <h2>核心成果線</h2>
                    <p>四條最接近「今天能不能判讀」的成果，保留狀態、結論與資料日。</p>
                </header>
                <div class="ifl-grid">
                    <?php foreach ($dashboard_products as $product): ?>
                        <?php $product_status = self::status_class($product['status'] ?? 'unknown'); ?>
                        <article class="ifl-card">
                            <span class="ifl-status <?php echo esc_attr($product_status); ?>"><i class="ifl-dot"></i><?php echo esc_html($product['status'] ?? 'unknown'); ?></span>
                            <h3><?php echo esc_html($product['name'] ?? '未命名成果線'); ?></h3>
                            <p><?php echo esc_html($product['result'] ?? ''); ?></p>
                            <p>資料日：<?php echo esc_html($product['freshness'] ?? '未知'); ?></p>
                        </article>
                    <?php endforeach; ?>
                </div>
                <?php if (!$dashboard_products): ?><div class="ifl-empty">尚未收到核心成果線。</div><?php endif; ?>
            </section>

            <section class="ifl-section" id="ifl-workstreams">
                <header class="ifl-section-head">
                    <h2>18501 作戰模組</h2>
                    <p>把 18 個正式工作依決策用途分組；可搜尋名稱、成果或負責角色，也可只看警告。</p>
                </header>
                <div class="ifl-toolbar">
                    <input class="ifl-search" type="search" data-ifl-search placeholder="搜尋工作、成果或角色" aria-label="搜尋正式工作">
                    <button class="ifl-filter is-active" type="button" data-ifl-filter="all">全部</button>
                    <button class="ifl-filter" type="button" data-ifl-filter="ready">正常</button>
                    <button class="ifl-filter" type="button" data-ifl-filter="warning">警告</button>
                    <button class="ifl-filter" type="button" data-ifl-filter="error">失敗</button>
                </div>
                <?php foreach ($jobs_by_category as $category => $category_jobs): ?>
                    <?php if (!$category_jobs) { continue; } ?>
                    <section class="ifl-category" data-ifl-category-group>
                        <div class="ifl-category-head">
                            <h3><?php echo esc_html($category); ?></h3>
                            <p><?php echo esc_html($category_descriptions[$category] ?? ''); ?></p>
                        </div>
                        <div class="ifl-job-grid">
                            <?php foreach ($category_jobs as $job): ?>
                                <?php
                                $job_status = self::status_class($job['status'] ?? 'unknown');
                                $search_text = implode(' ', [
                                    (string) ($job['name'] ?? ''),
                                    (string) ($job['owner'] ?? ''),
                                    (string) ($job['category'] ?? ''),
                                    (string) ($job['result'] ?? ''),
                                ]);
                                ?>
                                <article class="ifl-job" data-ifl-job data-status="<?php echo esc_attr($job_status); ?>" data-search="<?php echo esc_attr(strtolower($search_text)); ?>">
                                    <span class="ifl-status <?php echo esc_attr($job_status); ?>"><i class="ifl-dot"></i><?php echo esc_html($job['status'] ?? 'unknown'); ?></span>
                                    <h4><?php echo esc_html($job['name'] ?? '未命名工作'); ?></h4>
                                    <p><?php echo esc_html($job['result'] ?? ''); ?></p>
                                    <footer>
                                        <span><?php echo esc_html($job['owner'] ?? 'B4'); ?></span>
                                        <time><?php echo esc_html($job['freshness'] ?? '未知'); ?></time>
                                    </footer>
                                </article>
                            <?php endforeach; ?>
                        </div>
                    </section>
                <?php endforeach; ?>
                <?php if (!$dashboard_jobs): ?><div class="ifl-empty">尚未收到正式工作成果。</div><?php endif; ?>
                <p class="ifl-source-note">來源新鮮度：<?php echo esc_html($dashboard['source_freshness'] ?? '未知'); ?>。本區不含持倉、帳戶、個股清單、原始 log、cookies、secrets 或可執行指令。</p>
            </section>

            <section class="ifl-section" id="ifl-alerts">
                <header class="ifl-section-head">
                    <h2>需要先處理</h2>
                    <p>警示是可用性判讀的一部分；warning 不是整套不能用，而是該條成果需檢查新鮮度或來源。</p>
                </header>
                <?php if (!$alerts): ?>
                    <div class="ifl-empty">目前快照沒有高優先警示。</div>
                <?php else: ?>
                    <?php foreach ($alerts as $alert): ?>
                        <div class="ifl-alert <?php echo esc_attr(($alert['severity'] ?? '') === 'error' ? 'error' : ''); ?>">
                            <strong><?php echo esc_html($alert['title'] ?? '未命名警示'); ?></strong>
                            <span><?php echo esc_html($alert['detail'] ?? ''); ?></span>
                        </div>
                    <?php endforeach; ?>
                <?php endif; ?>
            </section>

            <section class="ifl-section" id="ifl-roles">
                <header class="ifl-section-head">
                    <h2>角色與功能檔案庫</h2>
                    <p>完整資料保留，但預設收合，避免 31 個角色與 16 個功能淹沒第一屏判讀。</p>
                </header>
                <details class="ifl-details">
                    <summary>角色運行成果（<?php echo esc_html((string) count($roles)); ?>）</summary>
                    <div class="ifl-grid">
                        <?php foreach ($roles as $role): ?>
                            <?php $status = self::status_class($role['status'] ?? 'unknown'); ?>
                            <article class="ifl-card">
                                <span class="ifl-status <?php echo esc_attr($status); ?>"><i class="ifl-dot"></i><?php echo esc_html($role['status'] ?? 'unknown'); ?></span>
                                <h3><?php echo esc_html(($role['id'] ?? '') . ' · ' . ($role['name'] ?? '')); ?></h3>
                                <p><?php echo esc_html($role['result'] ?? '尚無最近成果'); ?></p>
                                <p>證據：<?php echo esc_html($role['evidence'] ?? '未提供'); ?></p>
                            </article>
                        <?php endforeach; ?>
                    </div>
                    <?php if (!$roles): ?><div class="ifl-empty">尚未收到角色快照。</div><?php endif; ?>
                </details>
                <details class="ifl-details">
                    <summary>Investment OS 與系統功能（<?php echo esc_html((string) count($modules)); ?>）</summary>
                    <div class="ifl-grid">
                        <?php foreach ($modules as $module): ?>
                            <?php $status = self::status_class($module['status'] ?? 'unknown'); ?>
                            <article class="ifl-card">
                                <span class="ifl-status <?php echo esc_attr($status); ?>"><i class="ifl-dot"></i><?php echo esc_html($module['status'] ?? 'unknown'); ?></span>
                                <h3><?php echo esc_html($module['name'] ?? '未命名功能'); ?></h3>
                                <p><?php echo esc_html($module['summary'] ?? ''); ?></p>
                                <p>新鮮度：<?php echo esc_html($module['freshness'] ?? '未知'); ?></p>
                            </article>
                        <?php endforeach; ?>
                    </div>
                    <?php if (!$modules): ?><div class="ifl-empty">尚未收到功能快照。</div><?php endif; ?>
                </details>
            </section>

            <footer class="ifl-footer">資料由 Mac 主動推送去識別化摘要。WordPress 不保管 broker 憑證、API keys、cookies、持倉明細或可執行指令。</footer>
        </main>
        <script>
        (() => {
            const root = document.querySelector('.ifl-secretary');
            if (!root) return;
            const search = root.querySelector('[data-ifl-search]');
            const filters = [...root.querySelectorAll('[data-ifl-filter]')];
            const cards = [...root.querySelectorAll('[data-ifl-job]')];
            const groups = [...root.querySelectorAll('[data-ifl-category-group]')];
            let active = 'all';
            const apply = () => {
                const query = (search?.value || '').trim().toLowerCase();
                cards.forEach((card) => {
                    const statusMatch = active === 'all' || card.dataset.status === active;
                    const textMatch = !query || (card.dataset.search || '').includes(query);
                    card.hidden = !(statusMatch && textMatch);
                });
                groups.forEach((group) => {
                    group.hidden = !group.querySelector('[data-ifl-job]:not([hidden])');
                });
            };
            filters.forEach((button) => button.addEventListener('click', () => {
                active = button.dataset.iflFilter || 'all';
                filters.forEach((item) => item.classList.toggle('is-active', item === button));
                apply();
            }));
            search?.addEventListener('input', apply);
        })();
        </script>
        <?php
        return (string) ob_get_clean();
    }

    private static function snapshot(): array {
        $snapshot = get_option(self::OPTION_KEY, []);
        return is_array($snapshot) ? $snapshot : [];
    }

    private static function validate_snapshot(array $snapshot) {
        foreach (['generated_at', 'dashboard', 'roles', 'modules', 'alerts'] as $key) {
            if (!array_key_exists($key, $snapshot)) {
                return new WP_Error(
                    'ifl_snapshot_missing_field',
                    sprintf('Missing required field: %s', $key),
                    ['status' => 400]
                );
            }
        }
        if (!is_string($snapshot['generated_at']) || !is_array($snapshot['dashboard']) || !is_array($snapshot['roles']) || !is_array($snapshot['modules']) || !is_array($snapshot['alerts'])) {
            return new WP_Error(
                'ifl_snapshot_invalid_shape',
                'Snapshot fields have invalid types.',
                ['status' => 400]
            );
        }
        return true;
    }

    private static function sanitize_snapshot(array $snapshot): array {
        return [
            'generated_at' => sanitize_text_field($snapshot['generated_at']),
            'dashboard' => self::sanitize_dashboard($snapshot['dashboard']),
            'roles' => self::sanitize_rows($snapshot['roles'], ['id', 'name', 'status', 'result', 'evidence']),
            'modules' => self::sanitize_rows($snapshot['modules'], ['id', 'name', 'status', 'summary', 'freshness']),
            'alerts' => self::sanitize_rows($snapshot['alerts'], ['severity', 'title', 'detail']),
        ];
    }

    private static function sanitize_dashboard(array $dashboard): array {
        $clean = [];
        foreach (['status', 'verdict', 'detail', 'market_date', 'jobs_updated_at', 'source_freshness'] as $key) {
            if (isset($dashboard[$key]) && is_scalar($dashboard[$key])) {
                $clean[$key] = sanitize_text_field((string) $dashboard[$key]);
            }
        }
        $clean['kpis'] = self::sanitize_rows(
            isset($dashboard['kpis']) && is_array($dashboard['kpis']) ? $dashboard['kpis'] : [],
            ['label', 'value', 'status', 'detail']
        );
        $clean['market_indicators'] = self::sanitize_rows(
            isset($dashboard['market_indicators']) && is_array($dashboard['market_indicators']) ? $dashboard['market_indicators'] : [],
            ['id', 'name', 'value', 'change', 'status', 'freshness']
        );
        $clean['products'] = self::sanitize_rows(
            isset($dashboard['products']) && is_array($dashboard['products']) ? $dashboard['products'] : [],
            ['name', 'status', 'result', 'freshness']
        );
        $clean['jobs'] = self::sanitize_rows(
            isset($dashboard['jobs']) && is_array($dashboard['jobs']) ? $dashboard['jobs'] : [],
            ['id', 'name', 'owner', 'category', 'status', 'result', 'freshness']
        );
        return $clean;
    }

    private static function sanitize_rows(array $rows, array $allowed_keys): array {
        $clean = [];
        foreach (array_slice($rows, 0, 80) as $row) {
            if (!is_array($row)) {
                continue;
            }
            $item = [];
            foreach ($allowed_keys as $key) {
                if (isset($row[$key]) && is_scalar($row[$key])) {
                    $item[$key] = sanitize_text_field((string) $row[$key]);
                }
            }
            $clean[] = $item;
        }
        return $clean;
    }

    private static function status_class(string $status): string {
        $normalized = strtolower($status);
        if (in_array($normalized, ['ok', 'running', 'ready', 'verified'], true)) {
            return 'ok';
        }
        if (in_array($normalized, ['error', 'failed', 'broken', 'blocked'], true)) {
            return 'error';
        }
        return 'warning';
    }

    private static function private_response(array $data, int $status): WP_REST_Response {
        $response = new WP_REST_Response($data, $status);
        $response->header('Cache-Control', 'private, no-store, max-age=0');
        $response->header('X-Robots-Tag', 'noindex, nofollow, noarchive');
        return $response;
    }
}

register_activation_hook(__FILE__, [IFL_Personal_Secretary::class, 'activate']);
IFL_Personal_Secretary::boot();
