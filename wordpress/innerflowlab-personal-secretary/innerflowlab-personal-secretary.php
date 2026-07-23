<?php
/**
 * Plugin Name: InnerFlowLab Personal Secretary
 * Description: Private, read-only MAPLAB and Investment OS operations summary for the site owner.
 * Version: 0.2.0
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
        $dashboard_products = isset($dashboard['products']) && is_array($dashboard['products']) ? $dashboard['products'] : [];
        $dashboard_jobs = isset($dashboard['jobs']) && is_array($dashboard['jobs']) ? $dashboard['jobs'] : [];

        ob_start();
        ?>
        <style>
            .ifl-secretary{--ink:#10233f;--muted:#5f6f82;--line:#dfe7ef;--ok:#0e7a53;--warn:#ad6500;--bad:#b42318;max-width:1180px;margin:24px auto;padding:0 18px;color:var(--ink);font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
            .ifl-secretary *{box-sizing:border-box}.ifl-hero{padding:30px;border-radius:24px;background:linear-gradient(135deg,#0d1e36,#173d68);color:#fff;box-shadow:0 18px 42px rgba(16,35,63,.18)}
            .ifl-kicker{margin:0 0 8px;font-size:12px;letter-spacing:.14em;text-transform:uppercase;opacity:.72}.ifl-hero h1{margin:0;font-size:clamp(30px,5vw,54px);line-height:1}.ifl-hero p{max-width:760px;margin:14px 0 0;color:#dce9f7}
            .ifl-meta{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}.ifl-pill{display:inline-flex;align-items:center;padding:7px 11px;border-radius:999px;background:rgba(255,255,255,.1);font-size:13px}
            .ifl-section{margin-top:30px}.ifl-section h2{margin:0 0 14px;font-size:22px}.ifl-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}
            .ifl-card{border:1px solid var(--line);border-radius:18px;padding:18px;background:#fff;box-shadow:0 8px 24px rgba(16,35,63,.05)}.ifl-card h3{margin:0 0 8px;font-size:18px}.ifl-card p{margin:7px 0;color:var(--muted);font-size:14px;line-height:1.55}
            .ifl-status{display:inline-flex;align-items:center;gap:7px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.05em}.ifl-dot{width:9px;height:9px;border-radius:50%;background:#8796a8}.ifl-status.ok{color:var(--ok)}.ifl-status.ok .ifl-dot{background:var(--ok)}.ifl-status.warning{color:var(--warn)}.ifl-status.warning .ifl-dot{background:var(--warn)}.ifl-status.error{color:var(--bad)}.ifl-status.error .ifl-dot{background:var(--bad)}
            .ifl-alert{border-left:4px solid var(--warn);padding:12px 15px;margin:10px 0;background:#fff9ed;border-radius:0 12px 12px 0}.ifl-alert.error{border-color:var(--bad);background:#fff3f2}.ifl-alert strong{display:block;margin-bottom:4px}.ifl-empty{padding:22px;border:1px dashed #a9b9ca;border-radius:16px;color:var(--muted);background:#f8fafc}
            .ifl-verdict{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px;align-items:center;padding:22px;border:1px solid #f1d29c;border-radius:18px;background:#fff9ed}.ifl-verdict h3{margin:4px 0 8px;font-size:24px}.ifl-verdict p{margin:0;color:var(--muted)}.ifl-verdict-badge{min-width:110px;text-align:center;padding:12px 16px;border-radius:14px;background:#fff;color:var(--warn);font-weight:800}
            .ifl-kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:14px}.ifl-kpi{padding:15px;border:1px solid var(--line);border-radius:16px;background:#fff}.ifl-kpi small{display:block;color:var(--muted);margin-bottom:5px}.ifl-kpi strong{display:block;font-size:20px;margin-bottom:5px}.ifl-kpi span{display:block;color:var(--muted);font-size:12px;line-height:1.45}.ifl-kpi .ifl-status{display:inline-flex;margin-bottom:5px}
            .ifl-job-list{display:grid;gap:8px;margin-top:12px}.ifl-job{display:grid;grid-template-columns:minmax(190px,1.3fr) minmax(100px,.55fr) minmax(95px,.45fr) minmax(220px,1.7fr);gap:12px;align-items:center;padding:12px 14px;border:1px solid var(--line);border-radius:13px;background:#fff;font-size:13px}.ifl-job strong{font-size:14px}.ifl-job-owner,.ifl-job-fresh{color:var(--muted)}.ifl-details{margin-top:16px;border:1px solid var(--line);border-radius:16px;background:#f8fafc;padding:0 16px}.ifl-details summary{cursor:pointer;padding:15px 0;font-weight:700}.ifl-source-note{margin-top:10px;color:var(--muted);font-size:12px}
            @media (max-width:720px){.ifl-verdict{grid-template-columns:1fr}.ifl-verdict-badge{text-align:left}.ifl-job{grid-template-columns:1fr 1fr}.ifl-job-result{grid-column:1/-1}}
            .ifl-footer{margin:28px 0 10px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:12px}
        </style>
        <main class="ifl-secretary">
            <section class="ifl-hero">
                <p class="ifl-kicker">InnerFlowLab · Private Operations</p>
                <h1>Page 的個人秘書</h1>
                <p>把 MAPLAB 角色、Investment OS 功能與真正可驗證的成果集中到一個只讀入口。燈號只代表最近一次有證據的狀態，不代表投資建議或自動下單。</p>
                <div class="ifl-meta">
                    <span class="ifl-pill">更新：<?php echo esc_html($snapshot['generated_at'] ?? '尚未同步'); ?></span>
                    <span class="ifl-pill">角色：<?php echo esc_html((string) count($roles)); ?></span>
                    <span class="ifl-pill">功能：<?php echo esc_html((string) count($modules)); ?></span>
                    <span class="ifl-pill">模式：只讀</span>
                </div>
            </section>

            <section class="ifl-section">
                <h2>18501 成果中心</h2>
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
                        <div class="ifl-verdict-badge">只讀鏡像</div>
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

                    <h3>四條核心成果線</h3>
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

                    <details class="ifl-details" open>
                        <summary>正式工作最近成果（<?php echo esc_html((string) count($dashboard_jobs)); ?>）</summary>
                        <div class="ifl-job-list">
                            <?php foreach ($dashboard_jobs as $job): ?>
                                <?php $job_status = self::status_class($job['status'] ?? 'unknown'); ?>
                                <div class="ifl-job">
                                    <strong><?php echo esc_html($job['name'] ?? '未命名工作'); ?></strong>
                                    <span class="ifl-status <?php echo esc_attr($job_status); ?>"><i class="ifl-dot"></i><?php echo esc_html($job['status'] ?? 'unknown'); ?></span>
                                    <span class="ifl-job-owner"><?php echo esc_html($job['owner'] ?? 'B4'); ?></span>
                                    <span class="ifl-job-result"><?php echo esc_html($job['result'] ?? ''); ?> · <?php echo esc_html($job['freshness'] ?? '未知'); ?></span>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </details>
                    <p class="ifl-source-note">來源新鮮度：<?php echo esc_html($dashboard['source_freshness'] ?? '未知'); ?>。此區不含持倉、帳戶、股票清單、原始 log 或可執行指令。</p>
                <?php endif; ?>
            </section>

            <section class="ifl-section">
                <h2>需要先處理</h2>
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

            <section class="ifl-section">
                <h2>角色運行成果</h2>
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
                <?php if (!$roles): ?><div class="ifl-empty">尚未收到角色快照。先在 Mac 執行 exporter 的 dry-run。</div><?php endif; ?>
            </section>

            <section class="ifl-section">
                <h2>Investment OS 與系統功能</h2>
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
                <?php if (!$modules): ?><div class="ifl-empty">尚未收到功能快照。網站不會直接連到 broker、SQLite 或本機 secrets。</div><?php endif; ?>
            </section>

            <footer class="ifl-footer">資料由 Mac 主動推送去識別化摘要。WordPress 不保管 broker 憑證、API keys、cookies、持倉明細或可執行指令。</footer>
        </main>
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
        $clean['products'] = self::sanitize_rows(
            isset($dashboard['products']) && is_array($dashboard['products']) ? $dashboard['products'] : [],
            ['name', 'status', 'result', 'freshness']
        );
        $clean['jobs'] = self::sanitize_rows(
            isset($dashboard['jobs']) && is_array($dashboard['jobs']) ? $dashboard['jobs'] : [],
            ['id', 'name', 'owner', 'status', 'result', 'freshness']
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
