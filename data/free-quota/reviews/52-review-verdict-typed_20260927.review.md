# 換模型審稿 52-review-verdict-typed.job.md
產稿=nvidia/nemotron-3-super-120b-a12b:free 審稿=dots-studio/dots-3-note-preview:free 產出=data/free-quota/outputs/review-verdict-typed-spec.md

VERDICT: ISSUES

1) 草稿完全未提及任务要求的判定值（PASS/FAIL/NEEDS_HUMAN）及其定义，无任何理由码表，缺少至少8码的详细说明与触发条件。
2) 草稿未定义单行JSON输出格式，无verdict、reason_codes、note等字段的JSON Schema式说明。
3) 草稿未使用内部文件（即CONTEXT中的散文式审稿意见）改写为3个符合规格的示例判定（一个PASS、一个FAIL、一个NEEDS_HUMAN），完全未引用内部文件。
4) 草稿未列出「下放条件」，缺少关于哪些判定可纯程式做（关键字/正则表达式）、哪些留给免费模型、哪些必须NEEDS_HUMAN升级的说明。
5) 草稿仅输出「文件未提及」四字，未提供任何实质内容，严重偏离任务要求的5点规格设计，等同于未完成任务。
6) 草稿虽写了「文件未提及」，但并非针对内部文件中未记载的细节老实标注，而是整体放弃任务，属理解错误与输出缺失。

改进建议：应严格按照任务要求的5点重新编写完整规格，重点依据提供的内部文件（review.md）作为CONTEXT改写3个示例判定，并补全理由码表、JSON格式与下放条件。
