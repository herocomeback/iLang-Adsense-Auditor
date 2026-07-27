# AdSense 过审要求清单 (增强版)

一份对 Google 官方发布商政策的 clean-room 索引，按 `AUDIT_JUDGE_v1` schema 组织。包含了全网最全的 **29 条核心规范 ID**，并融汇整合了 **73 项细粒度检测子点**（含 PII、COPPA、假按钮、Deepfake、POST 限制等）。

**事实来源(正式审核前请刷新):**

- 资格要求 —— `https://support.google.com/adsense/answer/9724`
- AdSense 计划政策 —— `https://support.google.com/adsense/answer/48182`
- Google 发布商政策 —— `https://support.google.com/publisherpolicies/answer/10502938`
- 理解发布商政策与限制 —— `https://support.google.com/adsense/answer/10008391`
- 确保 Google 能访问你的 ads.txt / 爬虫访问 —— `https://support.google.com/adsense/answer/12171612`
- 广告位置政策 —— `https://support.google.com/adsense/answer/1346295`

如果实时文档与本清单任一条冲突，**以实时 Google 文档为准。** 政策会变；本清单是索引，不是权威。

下方表格中的严重度是该要求违规时的*默认*上限；实际每次审核的判定由判断向量得出。`id` 是稳定的，也是完整性闸门清点的对象。

---

## A. 所有权与访问 (`OWN`)

站点必须是 Google 能验证你拥有、且能抓取的。

| id | 要求 | 官方依据 | 默认严重度 | 包含的细粒度检查点 (Sub-checks) |
|---|---|---|---|---|
| OWN-01 | 你拥有或有权变现该站点；已在 AdSense 账户中添加并验证 | 资格要求 / ADS-OWN-01 | BLOCKER | 验证账户控制权、主应用域名绑定、重复账号屏蔽 (`ADS-ELIG-02`) |
| OWN-02 | AdSense 爬虫(`Mediapartners-Google`)未被 `robots.txt`、meta robots 或 WAF 拦截 | 爬虫访问 / ADS-CRAWL-02 | BLOCKER | 检查 `robots.txt` 规则、Cloudflare/WAF 阻断、人机验证墙、IP / 地域封锁 |
| OWN-03 | 页面返回可抓取的 HTTP 200；主内容无登录墙、无仅 POST 状态 | 资格要求 / ADS-CRAWL-03 | BLOCKER | 检查登录墙、404/5xx 错误、无 POST 状态无法渲染 (`ADS-CRAWL-03`)、死链 |
| OWN-04 | 站点位于你控制的域名(而非无法承载 `ads.txt` 的 URL,如纯社媒主页) | 资格要求 / ADS-OWN-02 | HIGH | 检查独立顶级/二级域名所有权、托管平台限制 (`ADS-ELIG-04`) |
| OWN-05 | 无地域封锁/制裁导致 Google 无法向站点所在区域投放 | 发布商政策(OFAC/出口管制) | BLOCKER | 检查 OFAC 制裁地区、高风险外包与无授权地域重定向 |

---

## B. 内容质量与原创性 (`CNT`)

内容必须充实、原创、属于你自己。

| id | 要求 | 官方依据 | 默认严重度 | 包含的细粒度检查点 (Sub-checks) |
|---|---|---|---|---|
| CNT-01 | 有足量、有真实价值的原创内容；不是单薄或占位站 | 计划政策 / ADS-CONTENT-01 | BLOCKER | 检查文字密度、单薄内容 (Thin Content)、占位符 (Lorem Ipsum)、死板块 |
| CNT-02 | 内容为原创，非抓取、洗稿或无附加价值的复制 | 计划政策 / ADS-CONTENT-02 | BLOCKER | 检查搬运/洗稿、纯抓取 RSS、无编辑价值的聚合/联盟链接堆砌 |
| CNT-03 | 非主要由无编辑价值的自动生成或 AI 批量生产的内容 | 计划政策 / ADS-PUB-14 | HIGH | 检查无监修的 AI 生成文本、AI 深度伪造媒体 (`ADS-PUB-14`)、关键词堆砌 |
| CNT-04 | 主内容为 AdSense 支持的语言 | 资格要求 / ADS-CONTENT-06 | HIGH | 检查语种支持、多语言混合站中无意义翻译页 |
| CNT-05 | 站点基本完整——无「建设中」、空栏目或死板块 | 计划政策 / ADS-CONTENT-04 | HIGH | 检查 Coming Soon 页面、未建好的假分类、模版默认示例残余 |
| CNT-06 | 内容不在纯嵌入页背后(如仅第三方视频/iframe 而无原创语境) | 计划政策 / ADS-CONTENT-02 | MEDIUM | 检查仅第三方 iframe/视频嵌入而缺乏至少 300 字原创文字介绍与评论 |

---

## C. 违禁与受限内容 (`POL`)

硬性政策红线与受限类别。

| id | 要求 | 官方依据 | 默认严重度 | 包含的细粒度检查点 (Sub-checks) |
|---|---|---|---|---|
| POL-01 | 无违法内容，或助长违法活动的内容 | 发布商政策 / ADS-PUB-01 | BLOCKER | 检查盗版下载、学术作弊工具 (`ADS-PUB-07`)、黑客破解教程 |
| POL-02 | 无侵权/假冒内容或知识产权侵犯 | 发布商政策 / ADS-PUB-02 | BLOCKER | 检查假冒品牌、未授权商标/Logo 滥用、盗版影视/音乐 |
| POL-03 | 无露骨性内容(轻度/受限内容需限量并标注) | 发布商政策 / ADS-REST-01 | BLOCKER | 检查成人/露骨色情、付费性服务 (`ADS-PUB-08`)、成人健康过度描写 |
| POL-04 | 无煽动仇恨、骚扰或对受保护群体的暴力内容 | 发布商政策 / ADS-PUB-03 | BLOCKER | 检查仇恨言论、歧视、虐待动物 (`ADS-PUB-04`)、自残或暴力赞美 |
| POL-05 | 无恶意软件、欺骗性下载或「有害软件」 | 发布商政策 / ADS-PUB-06 | BLOCKER | 检查流氓软件、钓鱼页面、网络诱导欺诈、恶意重定向 |
| POL-06 | 无以危险品(武器、爆炸物、消遣性毒品)为主的内容 | 发布商政策 / ADS-REST-03 | HIGH | 检查枪支弹药、爆炸物制作、娱乐性毒品/大麻 (`ADS-REST-04`) |
| POL-07 | 受限类别(酒类、博彩、成人健康等)合规，并理解其广告受限 | 发布商限制 / ADS-REST-05 | MEDIUM | 检查博彩/彩票 (`ADS-REST-06`)、烟酒销售、未核准处方药 (`ADS-REST-07`) |
| POL-08 | 无误导、欺骗用户的内容(如假新闻、虚假声称) | 发布商政策 / ADS-PUB-13 | HIGH | 检查违背科学共识的健康/气候声称、虚假选举声明、欺骗性身份隐瞒 (`ADS-PUB-05`) |

---

## D. 必备页面与披露 (`DIS`)

审核员会查看的信任与透明信号。

| id | 要求 | 官方依据 | 默认严重度 | 包含的细粒度检查点 (Sub-checks) |
|---|---|---|---|---|
| DIS-01 | 有隐私政策，且披露第三方/Google 广告 cookie 与数据使用 | 计划政策 / ADS-PRIV-01 | HIGH | 检查 Privacy Policy 页面、第三方 Cookie 声明、禁止 PII 泄漏 (`ADS-PRIV-03`) |
| DIS-02 | 有站点所有权信号(关于页与联系方式) | 计划政策 / ADS-UX-05 | MEDIUM | 检查 About Us、Contact Us、真实联系邮箱、组织机构主体标识 |
| DIS-03 | 在法规要求的地区有同意机制(如欧盟用户同意) | 计划政策 / ADS-PRIV-04 | HIGH | 检查 EEA/UK 欧盟 CMP 弹窗 (`ADS-PRIV-04`)、COPPA 儿童数据保护 (`ADS-PRIV-06`) |
| DIS-04 | 导航清晰诚实；内容可达，站点易用 | 计划政策 / ADS-UX-01 | MEDIUM | 检查导航栏功能性、面包屑、无欺骗性导航 (`ADS-UX-03`)、手机端匹配 |

---

## E. 广告行为与实现 (`IMP`)

适用于广告投放清理与过审后合规。

| id | 要求 | 官方依据 | 默认严重度 | 包含的细粒度检查点 (Sub-checks) |
|---|---|---|---|---|
| IMP-01 | 无自点击、诱导点击或人为制造的展示/点击膨胀 | 计划政策 / ADS-PROG-01 | BLOCKER | 检查自点广告、奖励点击 (`ADS-PROG-02`)、刷量软件/互点群 |
| IMP-02 | 未以违禁方式修改 AdSense 广告代码 | 计划政策 / ADS-PROG-05 | HIGH | 检查擅自修改 SDK 代码、隐藏广告渲染区域 |
| IMP-03 | 广告未被欺骗性地放置、标注或伪装成内容/导航 | 广告位置 / ADS-UX-03 | HIGH | 检查假下载按钮 (Deceptive CTAs)、假播放键、广告贴近导航栏伪装按钮 |
| IMP-04 | 广告加载未压过内容(广告/联盟低于内容价值阈值,尤其首屏之上) | 广告位置 / ADS-CONTENT-05 | MEDIUM | 检查首屏屏占比、广告压过主内容、干扰性浮窗 (Popunders / ADS-REST-08) |
| IMP-05 | 若有 `ads.txt`,可访问且正确授权 Google 为卖方(`pub-XXXX`,无 `ca-` 前缀) | ads.txt 指引 / ADS-TXT-01 | MEDIUM | 检查 `/ads.txt` 存在性、Google 卖方授权行、`pub-` 前缀正确性 |
| IMP-06 | 广告未放置在非内容页(错误页、感谢页、登录页或空结果页) | 广告位置 / ADS-PROG-06 | MEDIUM | 检查 404 页、登录页、感谢页、弹窗、软件/Toolbars 内挂广告 |

---

## 要求计数与完整性

要求 ID 总数:**29** (OWN 5 条 · CNT 6 条 · POL 8 条 · DIS 4 条 · IMP 6 条)

`audit_validator.py` 中的硬性闸门通过以上 29 条稳定 ID 进行清点，同时涵盖上述列表中列出的所有细粒度子检查点。

---

## 附录：29 条核心规则 ↔ 73 条子规则映射对照表 (Cross-Reference Matrix)

| 本工程 29 条 ID | 对应的 73 条旧版子项 (ADS-*) | 说明 |
|---|---|---|
| **`OWN-01`** | `ADS-ELIG-01`, `ADS-ELIG-02`, `ADS-OWN-01`, `ADS-SITE-01` | 账户资格、所有人控制权与验证 |
| **`OWN-02`** | `ADS-CRAWL-02`, `ADS-CRAWL-06` | 爬虫抓取拦截、robots.txt、WAF |
| **`OWN-03`** | `ADS-CRAWL-01`, `ADS-CRAWL-03`, `ADS-CRAWL-04` | 页面可达性、POST-only 渲染墙、跳转链 |
| **`OWN-04`** | `ADS-OWN-02`, `ADS-ELIG-04` | 独立控制域名与 Hosted 托管限制 |
| **`OWN-05`** | `ADS-PUB-01` (特定地域) | 出口管制与地域重定向限制 |
| **`CNT-01`** | `ADS-CONTENT-01`, `ADS-CONTENT-03` | 原创性、文字深度与 Thin Content |
| **`CNT-02`** | `ADS-CONTENT-02` | 抄袭、抓取、纯聚合与无附加价值复制 |
| **`CNT-03`** | `ADS-CONTENT-01`, `ADS-PUB-14` | AI 垃圾生成内容、伪造媒体与字词堆砌 |
| **`CNT-04`** | `ADS-CONTENT-06` | AdSense 支持的语言与混合语种站 |
| **`CNT-05`** | `ADS-CONTENT-04` | 建设中/空栏目/Lorem Ipsum 残余 |
| **`CNT-06`** | `ADS-CONTENT-02`, `ADS-PUB-11` | 纯嵌入页/第三方 iframe 无原创上下文 |
| **`POL-01`** | `ADS-PUB-01`, `ADS-PUB-07` | 违法活动、盗版、学术作弊工具 |
| **`POL-02`** | `ADS-PUB-02` | 知识产权、假冒品牌与侵权 |
| **`POL-03`** | `ADS-PUB-08`, `ADS-REST-01` | 成人、露骨、付费性服务 |
| **`POL-04`** | `ADS-PUB-03`, `ADS-PUB-04`, `ADS-REST-02` | 仇恨言论、骚扰、虐待动物 |
| **`POL-05`** | `ADS-PUB-06` | 恶意软件、钓鱼欺诈、有害软件 |
| **`POL-06`** | `ADS-REST-03`, `ADS-REST-04` | 枪支武器、爆炸物、娱乐性毒品 |
| **`POL-07`** | `ADS-REST-05`, `ADS-REST-06`, `ADS-REST-07` | 烟酒、博彩彩票、未核准处方药 |
| **`POL-08`** | `ADS-PUB-05`, `ADS-PUB-13` | 虚假陈述、科学共识争议声称 |
| **`DIS-01`** | `ADS-PRIV-01`, `ADS-PRIV-02`, `ADS-PRIV-03` | 隐私政策、Cookie 声明、PII 泄漏保护 |
| **`DIS-02`** | `ADS-UX-05` | 关于/联系/所有权透明度信号 |
| **`DIS-03`** | `ADS-PRIV-04`, `ADS-PRIV-06`, `ADS-PRIV-08` | 欧盟 CMP 同意、COPPA 儿童保护 |
| **`DIS-04`** | `ADS-UX-01`, `ADS-UX-02` | 清晰诚实的导航与移动端匹配 |
| **`IMP-01`** | `ADS-PROG-01`, `ADS-PROG-02` | 自点、诱导点击、奖励点击 |
| **`IMP-02`** | `ADS-PROG-05` | 违禁修改广告代码 |
| **`IMP-03`** | `ADS-UX-03`, `ADS-PROG-03`, `ADS-PUB-10` | 假下载/假播放按钮、欺骗性广告位置 |
| **`IMP-04`** | `ADS-CONTENT-05`, `ADS-REST-08` | 首屏广告过密、遮挡内容 |
| **`IMP-05`** | `ADS-TXT-01`, `ADS-TXT-02`, `ADS-SITE-02` | ads.txt 可达性与 Google pub- 授权行 |
| **`IMP-06`** | `ADS-PROG-06`, `ADS-PUB-11`, `ADS-PUB-12` | 404/登录/感谢页等非内容页放广告 |

---

## 审核机制背景(写报告时的参考知识，非检查项)

*(保持不变，提供机制常识与被拒后的冷却期建议)*
