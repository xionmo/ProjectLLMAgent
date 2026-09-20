# 第一单元 U00–U03 完整课件覆盖清单

共 96 页。备课完成不等于授课、独立掌握或模型实验完成。

回顾：此前已有讨论；补齐：补足计算链；预备：尚待逐项讲解；实验/自测：给出目标与验收，未伪造执行成绩。

| 页 | 单元 / 章节 | 分类 | 固定主题 |
| --- | --- | --- | --- |
| 1 | 导览 | 备课说明 | [第一单元：从调用边界到完整模型计算](unit-01-complete-slides.html#unit-cover) |
| 2 | 导览 | 完整导航 | [完整架构导航：每个计算块都有对应章节](unit-01-complete-slides.html#architecture-atlas) |
| 3 | U00 · 调用与系统 | 复习 | [语言模型输出，与工具真正执行，是两件事](unit-01-complete-slides.html#model-agent) |
| 4 | U00 · 调用与系统 | 复习 | [纠正信息进入上下文，不等于模型被训练了](unit-01-complete-slides.html#context-parameters) |
| 5 | U00 · 调用与系统 | 复习 | [图片数字算错：沿着证据定位第一次偏差](unit-01-complete-slides.html#trace-diagnosis) |
| 6 | U00 · 调用与系统 | 复习 | [把不同寿命的“状态”分开记账](unit-01-complete-slides.html#state-lifetimes) |
| 7 | U00 · 调用与系统 | 预备 | [图片输入也需要一条真实的数据通路](unit-01-complete-slides.html#image-pipeline) |
| 8 | U00 · 调用与系统 | 预备 | [一个实验先写清：改变什么，观察什么](unit-01-complete-slides.html#experiment-contract) |
| 9 | U01 · 概率与学习 | 复习 | [语言模型学习的是条件分布](unit-01-complete-slides.html#next-token) |
| 10 | U01 · 概率与学习 | 复习 | [logits：给每个候选一个实数分数](unit-01-complete-slides.html#vocabulary-logits) |
| 11 | U01 · 概率与学习 | 复习 | [softmax 把一组分数变成相对概率](unit-01-complete-slides.html#softmax-basics) |
| 12 | U01 · 概率与学习 | 复习 | [交叉熵：目标 token 获得了多少概率？](unit-01-complete-slides.html#cross-entropy) |
| 13 | U01 · 概率与学习 | 复习 | [梯度：损失对各个变量的局部变化率](unit-01-complete-slides.html#gradient-meaning) |
| 14 | U01 · 概率与学习 | 复习 | [输出梯度，怎样传回模型参数？](unit-01-complete-slides.html#gradient-chain) |
| 15 | U01 · 概率与学习 | 复习 | [梯度与参数更新量不是同一个量](unit-01-complete-slides.html#parameter-update) |
| 16 | U01 · 目标与数据 | 复习 | [输入与标签错开一位](unit-01-complete-slides.html#label-shift) |
| 17 | U01 · 目标与数据 | 复习 | [训练能并行预测，生成却依赖已生成的前缀](unit-01-complete-slides.html#teacher-forcing) |
| 18 | U01 · 目标与数据 | 复习 | [怎样检验“较早位置读不到未来”？](unit-01-complete-slides.html#causal-probe) |
| 19 | U01 · 目标与数据 | 预备 | [attention mask 与 loss mask 管的是不同事情](unit-01-complete-slides.html#loss-mask) |
| 20 | U01 · 目标与数据 | 预备 | [token 是编码单位，不一定是一个字或一个词](unit-01-complete-slides.html#tokenization) |
| 21 | U01 · 目标与数据 | 复习 | [评价前，先问测试到底独立在哪里](unit-01-complete-slides.html#split-generalization) |
| 22 | U01 · 目标与数据 | 预备 | [开放式问题有多个好答案，训练目标怎么理解？](unit-01-complete-slides.html#objective-choice) |
| 23 | U02 · 输入与架构 | 补齐 | [Encoder、Decoder 与 Encoder–Decoder](unit-01-complete-slides.html#architecture-types) |
| 24 | U02 · 输入与架构 | 补齐 | [Embedding：把离散 ID 查成可训练向量](unit-01-complete-slides.html#token-embedding) |
| 25 | U02 · 输入与架构 | 补齐 | [位置表示：让模型能区分排列与位置](unit-01-complete-slides.html#position-encoding) |
| 26 | U02 · 输入与架构 | 补齐 | [进入 Encoder 前：token 表示与位置表示相加](unit-01-complete-slides.html#input-representation) |
| 27 | U02 · 输入与架构 | 补齐 | [先给每根轴命名，再做张量变换](unit-01-complete-slides.html#tensor-notation) |
| 28 | U02 · Encoder 自注意力 | 补齐 | [Encoder self-attention：同一源序列提出查询并提供内容](unit-01-complete-slides.html#encoder-self-attention) |
| 29 | U02 · 注意力与归一化 | 复习 | [先分清：向量、分数、权重、读取结果](unit-01-complete-slides.html#symbols) |
| 30 | U02 · 注意力与归一化 | 复习 | [Q、K、V 从当前表示中投影出来](unit-01-complete-slides.html#qkv) |
| 31 | U02 · 注意力与归一化 | 复习 | [原始分数 → 缩放 → 遮罩 → 权重](unit-01-complete-slides.html#scores) |
| 32 | U02 · 分数缩放的推导 | 补齐 | [√dₖ 的推导，从假设和单个乘积项开始](unit-01-complete-slides.html#scaling-assumptions) |
| 33 | U02 · 分数缩放的推导 | 补齐 | [点积方差是 dₖ，标准差才是 √dₖ](unit-01-complete-slides.html#scaling-derivation) |
| 34 | U02 · 注意力与归一化 | 复习 | [因果遮罩规定信息从哪里可以流过来](unit-01-complete-slides.html#mask) |
| 35 | U02 · Encoder 自注意力 | 补齐 | [源位置的“后面”，也是已经给出的输入](unit-01-complete-slides.html#encoder-visibility) |
| 36 | U02 · 注意力与归一化 | 复习 | [权重乘整个 Value，再对来源求和](unit-01-complete-slides.html#weighted-read) |
| 37 | U02 · 注意力与归一化 | 复习 | [多头：同一批输入，多套读取方式](unit-01-complete-slides.html#multihead) |
| 38 | U02 · 注意力与归一化 | 复习 | [WO：组合各头读回来的特征](unit-01-complete-slides.html#output-projection) |
| 39 | U02 · 连贯 Encoder 算例 | 算例 | [给定一个能逐步核对的小型 Encoder 输入](unit-01-complete-slides.html#encoder-case-setup) |
| 40 | U02 · 连贯 Encoder 算例 | 算例 | [从 Q/K/V 算到 A，再真正读回内容](unit-01-complete-slides.html#encoder-case-attention) |
| 41 | U02 · 注意力与归一化 | 复习 | [Add：保留输入的直接贡献，再加子层输出](unit-01-complete-slides.html#residual) |
| 42 | U02 · 注意力与归一化 | 复习 | [LayerNorm：先对一个位置的特征做标准化](unit-01-complete-slides.html#layernorm-stats) |
| 43 | U02 · 注意力与归一化 | 复习 | [完整 LayerNorm 还会学习缩放和平移](unit-01-complete-slides.html#layernorm-affine) |
| 44 | U02 · 注意力与归一化 | 复习 | [三个操作，三种目的](unit-01-complete-slides.html#normalization-purpose) |
| 45 | U02 · 注意力与归一化 | 复习 | [归一化会改变信息，需要判断得失](unit-01-complete-slides.html#normalization-tradeoffs) |
| 46 | U02 · Encoder 第一次残差 | 补齐 | [Encoder 第一次 Add & Norm 产出 YE](unit-01-complete-slides.html#encoder-attention-addnorm) |
| 47 | U02 · 连贯 Encoder 算例 | 算例 | [延续同一组数值：相加，再逐行归一化](unit-01-complete-slides.html#encoder-case-addnorm) |
| 48 | U02 · 完整 Encoder | 补齐 | [先走完左边：这四步合起来才是一层](unit-01-complete-slides.html#encoder-route) |
| 49 | U02 · 完整 Encoder | 补齐 | [Feed Forward：进一步处理每个位置的特征](unit-01-complete-slides.html#encoder-ffn) |
| 50 | U02 · 完整 Encoder | 补齐 | [FFN 的三步：扩展、激活、组合回主干](unit-01-complete-slides.html#ffn-shapes) |
| 51 | U02 · 完整 Encoder | 补齐 | [为什么中间要放 ReLU？](unit-01-complete-slides.html#ffn-nonlinearity) |
| 52 | U02 · 完整 Encoder | 补齐 | [第二个 Add & Norm：加回 FFN 自己的输入](unit-01-complete-slides.html#encoder-second-norm) |
| 53 | U02 · 连贯 Encoder 算例 | 算例 | [给定 FFN 的两组矩阵，逐步得到 FE](unit-01-complete-slides.html#encoder-case-ffn) |
| 54 | U02 · 连贯 Encoder 算例 | 算例 | [第二次 Add & Norm，完成这一层](unit-01-complete-slides.html#encoder-case-output) |
| 55 | U02 · 完整 Encoder | 补齐 | [一层的输出，继续成为下一层的输入](unit-01-complete-slides.html#encoder-stack) |
| 56 | U02 · 完整 Encoder | 补齐 | [现在可以从源 token 一直追到 C](unit-01-complete-slides.html#encoder-summary) |
| 57 | U02 · Decoder 计算链 | 预备 | [Decoder 输入的是已知目标前缀的表示](unit-01-complete-slides.html#decoder-input) |
| 58 | U02 · Decoder 计算链 | 预备 | [Decoder self-attention：三路都来自目标侧，读取受因果约束](unit-01-complete-slides.html#decoder-self-attention) |
| 59 | U02 · Decoder 计算链 | 预备 | [Decoder 第一个 Add & Norm：先形成 Y₁](unit-01-complete-slides.html#decoder-first-norm) |
| 60 | U02 · Decoder 与交叉读取 | 接回 | [交叉注意力：查询与内容来自不同序列](unit-01-complete-slides.html#cross-sources) |
| 61 | U02 · Decoder 与交叉读取 | 接回 | [权重矩阵可以是长方形](unit-01-complete-slides.html#cross-shapes) |
| 62 | U02 · Decoder 与交叉读取 | 接回 | [“后面的源位置”不等于“未来目标”](unit-01-complete-slides.html#cross-mask) |
| 63 | U02 · Decoder 计算链 | 预备 | [第二个 Add & Norm：把跨序列读取结果加回 Y₁](unit-01-complete-slides.html#decoder-cross-norm) |
| 64 | U02 · Decoder 计算链 | 预备 | [Decoder 的 FFN：对融合后的目标表示逐位置计算](unit-01-complete-slides.html#decoder-ffn) |
| 65 | U02 · Decoder 计算链 | 预备 | [第三个 Add & Norm：完成这一 Decoder 层](unit-01-complete-slides.html#decoder-last-norm) |
| 66 | U02 · Decoder 计算链 | 预备 | [完整 Decoder 层：三条子层与三条残差路径](unit-01-complete-slides.html#decoder-block) |
| 67 | U02 · 从特征到输出 | 预备 | [最终表示如何变成词表 logits？](unit-01-complete-slides.html#vocabulary-head) |
| 68 | U02 · 课程实现选择 | 预备 | [课程初版：decoder-only、pre-LN、GELU](unit-01-complete-slides.html#decoder-only) |
| 69 | U03 · 手写实现 | 预备 | [手写模型：每次只增加已经能解释的部件](unit-01-complete-slides.html#implementation-plan) |
| 70 | U03 · 手写实现 | 预备 | [训练开始前，参数先要有一个数值起点](unit-01-complete-slides.html#initialization) |
| 71 | U03 · 手写实现 | 代码卡 | [用基础张量操作对应已学的注意力公式](unit-01-complete-slides.html#attention-code) |
| 72 | U03 · 手写实现 | 代码卡 | [一个 pre-LN block 的计算顺序](unit-01-complete-slides.html#preln-code) |
| 73 | U03 · 训练与恢复 | 预备 | [一次训练迭代：哪个动作真正更新了权重？](unit-01-complete-slides.html#training-loop) |
| 74 | U03 · 训练与恢复 | 预备 | [AdamW 还保存梯度统计，恢复训练时也要保存它们](unit-01-complete-slides.html#adamw) |
| 75 | U03 · 训练与恢复 | 预备 | [Dropout 与运行模式：为什么做核对时先关闭随机层？](unit-01-complete-slides.html#dropout) |
| 76 | U03 · 训练与恢复 | 实验卡 | [先让一个小批次学得动，再讨论泛化](unit-01-complete-slides.html#tiny-overfit) |
| 77 | U03 · 训练与恢复 | 预备 | [梯度累积要对应同一个总目标](unit-01-complete-slides.html#gradient-accumulation) |
| 78 | U03 · 训练与恢复 | 预备 | [恢复训练需要的不只是模型参数](unit-01-complete-slides.html#checkpoint) |
| 79 | U03 · 生成与缓存 | 预备 | [生成循环：先处理前缀，再一次次追加 token](unit-01-complete-slides.html#generation) |
| 80 | U03 · 生成与缓存 | 预备 | [KV 缓存复用的是过去位置已经算出的 K、V](unit-01-complete-slides.html#kv-cache) |
| 81 | U03 · 生成与缓存 | 预备 | [带缓存时，因果边界包含前缀偏移](unit-01-complete-slides.html#cache-offset) |
| 82 | U03 · 生成与缓存 | 实验卡 | [先证明同一前缀的结果一致，再比较速度](unit-01-complete-slides.html#cache-equivalence) |
| 83 | U03 · 资源与性能 | 预备 | [显存账：权重装得下，运行也可能装不下](unit-01-complete-slides.html#memory-budget) |
| 84 | U03 · 资源与性能 | 预备 | [从 CPU 优化经验，迁移到 GPU 的问题清单](unit-01-complete-slides.html#cpu-to-cuda) |
| 85 | U03 · 资源与性能 | 实验卡 | [计时先写清边界](unit-01-complete-slides.html#benchmarking) |
| 86 | 自测与实验 | 实验卡 | [让每个实验都有能被推翻的预测](unit-01-complete-slides.html#experiment-matrix) |
| 87 | 论文与发展脉络 | 预备 | [怎样把《Attention Is All You Need》读成证据链？](unit-01-complete-slides.html#paper-reading) |
| 88 | 论文与发展脉络 | 拓展 | [归一化的发展：拆开设计问题，再做对照](unit-01-complete-slides.html#normalization-history) |
| 89 | 论文与发展脉络 | 拓展 | [两类效率改进：实现同一计算，或改变模型结构](unit-01-complete-slides.html#attention-efficiency) |
| 90 | 论文与发展脉络 | 拓展 | [“并行预测再纠正”包含不同路线](unit-01-complete-slides.html#parallel-generation) |
| 91 | 图片输入的下一步 | 预备 | [图像特征如何进入语言模型？](unit-01-complete-slides.html#image-next) |
| 92 | 自测与实验 | 自测 | [U00–U01：先解释证据和目标](unit-01-complete-slides.html#test-u00-u01) |
| 93 | 自测与实验 | 自测 | [用计算依赖来检查理解](unit-01-complete-slides.html#review) |
| 94 | 自测与实验 | 自测 | [U03：用失败对照证明检查有用](unit-01-complete-slides.html#test-u03) |
| 95 | 自测与实验 | 实验卡 | [第一单元的验收，需要哪些独立证据？](unit-01-complete-slides.html#delivery-state) |
| 96 | 原始来源与接续 | 参考 | [按问题回到原始来源](unit-01-complete-slides.html#source-index) |

原 24 页回顾版的页面 ID 和页序保持不变。完整版独立保存阅读位置，架构图各模块链接到固定章节。

已提供：定义、公式、作用、形状、数值算例、问题与答案、实现阅读卡、实验验收与原始来源。

实验边界：本次完成文档、确定性小矩阵算例与页面验证；课程教学模型训练、CUDA 性能与真实图片模型实验仍须按 E01/V01 实施。

源码：unit01/ 下的补充页面与公式；构建：python3 scripts/build_unit01_slides.py。
