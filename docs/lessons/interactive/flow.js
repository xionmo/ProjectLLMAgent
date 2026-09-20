(() => {
  const NS='http://www.w3.org/2000/svg',XHTML='http://www.w3.org/1999/xhtml';
  const motion=matchMedia('(prefers-reduced-motion: reduce)');
  const N=(id,label,col,row,stage,detail='')=>({id,label,col,row,stage,detail});
  const E=(from,to,route='')=>({from,to,route});
  const chain=(title,items)=>({title,nodes:items.map((item,i)=>N('n'+i,item[0],i,0,i,item[1])),edges:items.slice(1).map((_,i)=>E('n'+i,'n'+(i+1))),steps:items.map(item=>item[1])});
  const residualNorm=(title,input,branch,update,normalizer,output)=>({title,nodes:[N('in',input,0,1,0),N('branch',branch,1,0,1),N('update',update,2,0,1),N('add',input+' + '+update,3,1,2),N('norm',normalizer,4,1,3),N('out',output,5,1,4)],edges:[E('in','branch'),E('branch','update'),E('update','add'),E('in','add','low'),E('add','norm'),E('norm','out')],steps:['本子层的输入同时进入主路和恒等旁路。','主路根据自己的参数计算子层输出。','把子层输出加回它自己的输入。','这一处 LayerNorm 计算当前统计量并应用自己的参数。','结果成为下一个子层的输入，位置数与主干宽度保持一致。']});
  const flows={
    attention:{title:'显微结构：Q/K 匹配，V 沿另一条路径汇入',nodes:[N('h','H：整段表示',0,1,0),N('q','Q',1,0,1),N('k','K',1,1,1),N('v','V',1,2,1),N('a','分数 → A',2,0.5,2),N('o','O = AV',3,1,3),N('u','组合 → U',4,1,4)],edges:[E('h','q'),E('h','k'),E('h','v'),E('q','a'),E('k','a'),E('a','o'),E('v','o','low'),E('o','u')],steps:['每个位置既可提出查询，也可提供被读取的表示。','三路投影分别形成 Q、K、V。','Q/K 匹配、缩放，并按该模块的可见性规则归一化。','权重 A 与内容 V 在这一步汇合；V 不参与前面的点积。','各头组合并经 W_O，得到子层输出。']},
    qkv:{title:'显微结构：一个输入表示，三路参数投影',nodes:[N('h','H：输入表示',0,1,0),N('q','Q = HW_Q',1,0,1,'查询向量由输入和 W_Q 产生。'),N('k','K = HW_K',1,1,1,'Key 用于匹配；不是注意力权重。'),N('v','V = HW_V',1,2,1,'Value 提供后续要汇总的内容。')],edges:[E('h','q'),E('h','k'),E('h','v')],steps:['先明确输入 H 的位置数和特征宽度。','三路投影可以独立计算；同一头在不同位置共享各自的参数。']},
    scores:chain('显微结构：匹配分数怎样变成读取权重',[
      ['Q、K','两个向量的同一特征维度用于匹配。'],['QKᵀ','点积结果是每个 query 对每个 key 的标量分数。'],['÷ √dₖ','按维度补偿典型分数尺度；不在这里求样本均值。'],['+ M','给不允许读取的位置加负无穷。'],['softmax','固定 query，沿来源位置归一化。'],['A：读取权重','每行非负且和为 1，接下来用它混合 V。']]),
    mask:chain('显微结构：mask 作用于 softmax 之前',[
      ['分数 S','负分数仍是合法匹配分数。'],['加性遮罩 M','允许位置加 0，禁止位置加负无穷。'],['S + M','保留允许来源的分数；禁止项变为负无穷。'],['softmax','在允许来源之间重新归一化。'],['A','禁止来源的权重变为 0。']]),
    read:{title:'显微结构：权重与内容在读取时汇合',nodes:[N('a','A：权重',0,0,0),N('v','V：内容',0,2,0),N('part','a_ij v_j',1,1,1),N('sum','对 j 求和',2,1,2),N('out','O = AV',3,1,3)],edges:[E('a','part'),E('v','part'),E('part','sum'),E('sum','out')],steps:['A 与 V 是不同对象：系数与特征向量。','一个标量 a_ij 缩放整个 v_j，得到单个来源的贡献。','把允许来源的贡献相加。','每个 query 得到一个读取结果；输出宽度由 V 决定。']},
    heads:{title:'显微结构：多头并行读取，再组合',nodes:[N('h','H',0,1,0),N('h1','Head 1',1,0,1),N('h2','Head 2',1,2,1),N('cat','Concat',2,1,2),N('wo','W_O',3,1,3),N('out','U',4,1,4)],edges:[E('h','h1'),E('h','h2'),E('h1','cat'),E('h2','cat'),E('cat','wo'),E('wo','out')],steps:['所有头接收这批位置的输入表示。','各头使用自己的投影参数和读取权重。','按特征方向拼接各头结果。','输出投影重新组合特征，回到主干宽度。','每个位置得到一个多头注意力子层输出。']},
    project:chain('显微结构：同一位置的多头特征组合',[
      ['各头 oᵢ','各个头的读取结果已经计算好。'],['Concat → c_i','拼接保留各头分量，不做求平均。'],['c_i W_O','可训练矩阵将分量组合到输出坐标。'],['u_i','宽度回到 d_model，供残差相加使用。']]),
    residual:{title:'显微结构：主路与恒等旁路在 Add 汇合',nodes:[N('h','h_i',0,1,0),N('sub','Attention',1,0,1),N('u','u_i',2,0,1),N('add','h_i + u_i',3,1,2),N('out','h̃_i',4,1,3)],edges:[E('h','sub'),E('sub','u'),E('u','add'),E('h','add','low'),E('add','out')],steps:['输入 h_i 同时进入主路，并沿旁路保留直接贡献。','注意力主路产生 u_i；这个子层输出不是原输入的副本。','两路按同一位置、同一特征分量相加。','得到 Add 的结果；完整 Add & Norm 后面还要做 LayerNorm。']},
    stats:chain('显微结构：LayerNorm 的统计与标准化',[
      ['h̃_i','取同一个位置的全部特征分量。'],['μ_i、σ²_i','计算这一向量自己的均值与方差。'],['减 μ_i','每个分量减去同一个中心。'],['÷ √(σ²_i+ε)','缩放到较规整的尺度；ε 避免分母为零。'],['标准化向量','这是 γ、β 变换之前的中间结果。']]),
    affine:chain('显微结构：标准化之后的可学习变换',[
      ['标准化向量','均值与方差已经由当前输入确定。'],['逐分量乘 γ','γ 是可训练的缩放向量。'],['逐分量加 β','β 是可训练的平移向量。'],['h′_i','最终输出不必保持均值为零或方差为一。']]),
    ffn:chain('显微结构：FFN 在每个位置内部处理特征',[
      ['Y_E','输入已经包含注意力汇入的上下文。'],['W₁、b₁','形成更宽的中间特征；token 位置数不变。'],['ReLU','逐分量引入非线性。课程初版 decoder 另用 GELU。'],['W₂、b₂','组合回主干宽度。'],['F_E','得到 FFN 子层输出，每行仍对齐原位置。']]),
    second:{title:'显微结构：第二次残差相加接的是 Y_E',nodes:[N('y','Y_E',0,1,0),N('ffn','FFN',1,0,1),N('f','F_E',2,0,1),N('add','Y_E + F_E',3,1,2),N('norm','LN_FFN',4,1,3),N('out','H_E next',5,1,4)],edges:[E('y','ffn'),E('ffn','f'),E('f','add'),E('y','add','low'),E('add','norm'),E('norm','out')],steps:['Y_E 是 FFN 的输入，也是这条旁路的起点。','同一组 FFN 参数逐位置作用，产生 F_E。','F_E 加回自己的输入 Y_E。','这一处 LayerNorm 重新计算统计量并使用自己的参数。','形成一层 Encoder 的输出，接到下一层。']},
    encoder:{title:'显微结构：一个完整 Encoder 层',nodes:[N('h','H_E',0,1,0),N('attn','Self-Attention',1,0,1),N('n1','Add & Norm 1',2,1,2),N('ffn','FFN',3,0,3),N('n2','Add & Norm 2',4,1,4)],edges:[E('h','attn'),E('attn','n1'),E('h','n1','low'),E('n1','ffn'),E('ffn','n2'),E('n1','n2','low')],steps:['进入这一层的整段源表示。','源位置之间读取已知上下文。','注意力输出加回 H_E，得到 Y_E。','逐位置执行非线性特征变换。','FFN 输出加回 Y_E，形成下一层输入。']},
    decoder:{title:'显微结构：原论文的一层 Decoder',nodes:[N('h','H：目标侧',0,1,0),N('a','因果自注意力',1,0,1),N('n1','Add & Norm 1',2,1,2),N('c','C：源侧',2,2,0),N('cross','交叉注意力',3,0,3),N('n2','Add & Norm 2',4,1,4),N('f','FFN',5,0,5),N('n3','Add & Norm 3',6,1,6)],edges:[E('h','a'),E('a','n1'),E('h','n1','low'),E('n1','cross'),E('c','cross'),E('cross','n2'),E('n1','n2','low'),E('n2','f'),E('f','n3'),E('n2','n3','low')],steps:['目标表示 H 与已知的 Encoder 输出 C 是不同来源。','先在目标侧作因果读取。','第一处残差归一化形成 Y₁。','用 Y₁ 查询 C，读取源信息。','将交叉读取结果加回 Y₁。','逐位置处理融合后的特征。','第三处残差归一化形成本层输出。']},
    decoderffn:chain('显微结构：Decoder 的逐位置 FFN',[
      ['Y₂','已经融合目标前缀与源信息的表示。'],['W₁、b₁','形成 Decoder 本层的中间特征。'],['ReLU','原论文在这里应用逐分量非线性。'],['W₂、b₂','回到主干宽度。'],['F','随后加回本次 FFN 输入 Y₂。']]),
    stack:chain('显微结构：完整层的堆叠',[
      ['H_E⁽⁰⁾','词嵌入与位置编码形成第一层输入。'],['Encoder 1','执行完整四步，得到第一层输出。'],['Encoder 2…N','重复相同结构，各层参数分别学习。'],['C = H_E⁽ᴺ⁾','最终仍是按源位置排列的上下文矩阵。']]),
    cross:{title:'显微结构：目标侧提问，源侧提供内容',nodes:[N('y','Y₁：目标',0,0,0),N('c','C：源',0,2,0),N('q','Q',1,0,1),N('k','K',1,1,1),N('v','V',1,2,1),N('a','QKᵀ → A',2,0.5,2),N('o','AV → O',3,1,3),N('u','组合 → Uc',4,1,4)],edges:[E('y','q'),E('c','k'),E('c','v'),E('q','a'),E('k','a'),E('a','o'),E('v','o','low'),E('o','u')],steps:['目标侧和源侧是两条不同序列。','Q 由 Y₁ 产生，K/V 由 C 产生。','每个目标 query 对源位置匹配并归一化。','读取源侧 V；结果的行数仍由 query 数决定。','多头组合后，用结果更新 Decoder 的表示。']},
    vocab:chain('显微结构：从隐藏表示到候选 token',[
      ['Decoder 输出','每个位置是 d 维特征。'],['词表投影','映射到词表大小，每一维对应一个候选。'],['logits Z','分数尚未归一化。'],['softmax / loss','推理形成候选分布；训练可直接把 logits 送入交叉熵。']]),
    train:chain('显微结构：一次参数更新',[
      ['输入、标签','按序列移位构造训练目标。'],['前向','用当前参数产生 logits。'],['loss','只对有效目标位置汇总损失。'],['backward','链式法则得到各参数梯度。'],['optimizer.step','优化器执行参数更新；前向本身不等于训练。']]),
    cache:{title:'显微结构：复用旧 K/V，计算当前 query',nodes:[N('h','新位置表示',0,0,0),N('old','已有 K/V',0,2,0),N('new','新 Q/K/V',1,0,1),N('keys','拼接 K/V',2,1,2),N('read','当前 Q 读取',3,1,3),N('out','输出、更新缓存',4,1,4)],edges:[E('h','new'),E('new','keys'),E('old','keys'),E('new','read','high'),E('keys','read'),E('read','out')],steps:['前缀不变、参数不变时，保留每层已有 K/V。','只为新增位置计算新的投影。','旧 K/V 与新增 K/V 按位置连接。','当前 query 使用正确的绝对位置和可见性。','产生本步输出，并保留增长后的缓存。']}
  };
  flows.ffnshapes=chain('显微结构：特征宽度变化，位置数保持不变',[
    ['4 × 512','4 个位置，每个位置的主干宽度为 512。'],['W₁ → 4 × 2048','第一次带偏置的线性变换扩展特征宽度。'],['ReLU：2048','ReLU 后仍为 4 × 2048；逐元素非线性保持形状。'],['W₂ → 4 × 512','回到主干宽度，供残差相加。']]);
  flows.encoderfirst=residualNorm('显微结构：Encoder 第一次 Add & Norm','H_E','Self-Attention','U_E','LN_attn','Y_E');
  flows.decoderfirst=residualNorm('显微结构：Decoder 第一次 Add & Norm','H','因果自注意力','Us','LN₁','Y₁');
  flows.decoderlast=residualNorm('显微结构：Decoder 第三次 Add & Norm','Y₂','FFN','F','LN₃','D_next');
  flows.crossnorm=residualNorm('显微结构：交叉读取结果加回 Y₁','Y₁','读取 C','Uc','LN₂','Y₂');
  flows.preln={title:'显微结构：课程初版的 pre-LN 残差路径',nodes:[N('h','H',0,1,0),N('ln1','LN₁',1,0,1),N('a','因果注意力',2,0,2),N('x','Add → X',3,1,3),N('ln2','LN₂',4,0,4),N('f','GELU FFN',5,0,5),N('out','Add → H_next',6,1,6)],edges:[E('h','ln1'),E('ln1','a'),E('a','x'),E('h','x','low'),E('x','ln2'),E('ln2','f'),E('f','out'),E('x','out','low')],steps:['保留未进入本子层归一化的 H 作为旁路。','先归一化主路输入。','注意力作用于 LN₁(H)。','注意力输出加回原 H，得到 X。','第二条主路先对 X 归一化。','GELU FFN 处理 LN₂(X)。','FFN 输出加回原 X；这与 post-LN 的顺序不同。']};
  const mapping={qkv:'qkv',scores:'scores',mask:'mask','weighted-read':'read',multihead:'heads','output-projection':'project',residual:'residual','layernorm-stats':'stats','layernorm-affine':'affine','encoder-route':'encoder','encoder-ffn':'ffn','ffn-shapes':'ffnshapes','ffn-nonlinearity':'ffn','encoder-second-norm':'second','encoder-stack':'stack','cross-sources':'cross','cross-shapes':'cross','cross-mask':'cross','encoder-self-attention':'attention','encoder-visibility':'mask','encoder-case-attention':'read','encoder-attention-addnorm':'encoderfirst','encoder-case-addnorm':'stats','encoder-case-ffn':'ffn','encoder-case-output':'second','decoder-self-attention':'attention','decoder-first-norm':'decoderfirst','decoder-cross-norm':'crossnorm','decoder-last-norm':'decoderlast','decoder-ffn':'decoderffn','decoder-block':'decoder','decoder-only':'preln','preln-code':'preln','vocabulary-head':'vocab','vocabulary-logits':'vocab','training-loop':'train','parameter-update':'train','kv-cache':'cache','cache-offset':'cache','cache-equivalence':'cache'};
  let active=null,raf=0,playing=false,elapsed=0,started=0;
  const panels=new Map();
  function make(tag,attrs,parent){const element=document.createElementNS(NS,tag);Object.entries(attrs||{}).forEach(([key,value])=>element.setAttribute(key,String(value)));if(parent)parent.appendChild(element);return element;}
  function readAuto(){try{return localStorage.getItem('lesson-micro-autoplay')!=='false';}catch{return true;}}
  let automatic=readAuto();
  function build(slide,type){
    const cfg=flows[type],branched=cfg.nodes.some(n=>n.row>0),maxCol=Math.max(...cfg.nodes.map(n=>n.col)),maxRow=Math.max(...cfg.nodes.map(n=>n.row));
    const width=(maxCol+1)*124+16,height=branched?126:48;
    const panel=document.createElement('div');panel.className='micro-flow'+(branched?' branched':'');panel.dataset.flow=type;
    panel.innerHTML='<div class="micro-head"><span></span><div class="micro-controls"><button type="button" data-flow-action="play">播放</button><button type="button" data-flow-action="prev">上一步</button><button type="button" data-flow-action="next">下一步</button><label><input type="checkbox" data-flow-auto>自动演示</label><span class="micro-hint">依赖示意 · 不表示耗时</span></div></div><div class="micro-viewport"></div><div class="micro-caption" aria-live="off"></div>';
    panel.querySelector('.micro-head>span').textContent=cfg.title;panel.querySelector('[data-flow-auto]').checked=automatic;
    const svg=make('svg',{viewBox:'0 0 '+width+' '+height,class:'micro-svg',role:'group','aria-label':cfg.title},panel.querySelector('.micro-viewport'));
    const defs=make('defs',{},svg),markerId='micro-arrow-'+slide.id,marker=make('marker',{id:markerId,viewBox:'0 0 8 8',refX:7,refY:4,markerWidth:5,markerHeight:5,orient:'auto'},defs);make('path',{d:'M 0 0 L 8 4 L 0 8 Z',fill:'#91a7aa'},marker);
    const pos=new Map(cfg.nodes.map(n=>[n.id,{x:8+n.col*124,y:branched?8+n.row*32:7,w:108,h:32,node:n}]));
    const edges=cfg.edges.map(edge=>{
      const a=pos.get(edge.from),b=pos.get(edge.to),sx=a.x+a.w,sy=a.y+a.h/2,tx=b.x,ty=b.y+b.h/2;
      const path=edge.route==='low'?'M '+sx+' '+sy+' L '+(sx+6)+' 118 L '+(tx-7)+' 118 L '+(tx-7)+' '+ty+' L '+tx+' '+ty:edge.route==='high'?'M '+sx+' '+sy+' L '+(sx+6)+' 2 L '+(tx-7)+' 2 L '+(tx-7)+' '+ty+' L '+tx+' '+ty:'M '+sx+' '+sy+' C '+(sx+12)+' '+sy+' '+(tx-12)+' '+ty+' '+tx+' '+ty;
      const element=make('path',{d:path,class:'micro-edge','marker-end':'url(#'+markerId+')'},svg);
      const packet=make('circle',{r:3.3,class:'micro-packet',visibility:'hidden'},svg);
      return {element,packet,stage:b.node.stage};
    });
    const nodes=cfg.nodes.map(n=>{
      const p=pos.get(n.id),fo=make('foreignObject',{x:p.x,y:p.y,width:p.w,height:p.h},svg),button=document.createElementNS(XHTML,'button');
      button.type='button';button.className='micro-node';button.textContent=n.label;button.setAttribute('aria-label',n.label+'；点击查看对应步骤');
      button.addEventListener('click',()=>{activate(panel,false);stop();active.stage=n.stage;show(n.detail||cfg.steps[n.stage]);});fo.appendChild(button);return {button,stage:n.stage};
    });
    const state={panel,cfg,edges,nodes,stage:0,caption:panel.querySelector('.micro-caption'),play:panel.querySelector('[data-flow-action="play"]')};panels.set(panel,state);
    panel.querySelector('[data-flow-action="play"]').addEventListener('click',()=>{if(active?.panel!==panel)activate(panel,false);if(playing)stop();else play(active.stage===cfg.steps.length-1);});
    panel.querySelector('[data-flow-action="prev"]').addEventListener('click',()=>{activate(panel,false);stop();active.stage=Math.max(0,active.stage-1);show();});
    panel.querySelector('[data-flow-action="next"]').addEventListener('click',()=>{activate(panel,false);stop();active.stage=Math.min(cfg.steps.length-1,active.stage+1);show();});
    panel.querySelector('[data-flow-auto]').addEventListener('change',event=>{automatic=event.target.checked;document.querySelectorAll('[data-flow-auto]').forEach(e=>e.checked=automatic);try{localStorage.setItem('lesson-micro-autoplay',String(automatic));}catch{}if(!automatic)stop();});
    slide.classList.add('has-micro');slide.querySelector('h1,h2').insertAdjacentElement('afterend',panel);
  }
  function show(override){if(!active)return;const {cfg,nodes,edges,stage,caption}=active;nodes.forEach(n=>{n.button.classList.toggle('active',n.stage===stage);n.button.classList.toggle('complete',n.stage<stage);});edges.forEach(e=>{e.element.classList.toggle('active',e.stage===stage);e.packet.setAttribute('visibility','hidden');});caption.textContent='步骤 '+(stage+1)+' / '+cfg.steps.length+'：'+(override||cfg.steps[stage]);active.play.textContent=playing?'暂停':stage===cfg.steps.length-1?'重播':'播放';}
  function stop(){if(raf)cancelAnimationFrame(raf);raf=0;playing=false;if(active)show();}
  function tick(now){if(!active||!playing)return;const duration=650,t=Math.min(1,(now-started+elapsed)/duration);if(!motion.matches)active.edges.filter(e=>e.stage===active.stage).forEach(e=>{const p=e.element.getPointAtLength(e.element.getTotalLength()*t);e.packet.setAttribute('cx',p.x);e.packet.setAttribute('cy',p.y);e.packet.setAttribute('visibility','visible');});if(t>=1){if(active.stage===active.cfg.steps.length-1){stop();return;}active.stage++;elapsed=0;started=now;show();}raf=requestAnimationFrame(tick);}
  function play(restart=false){if(!active)return;stop();if(restart)active.stage=0;elapsed=0;started=performance.now();playing=true;show();raf=requestAnimationFrame(tick);}
  function activate(panel,autoplay){if(active?.panel===panel)return;stop();active=panels.get(panel)||null;if(!active)return;active.stage=0;show();if(autoplay&&automatic&&!motion.matches&&!document.hidden)play();}
  function enter(){const slide=document.querySelector('.slide:not([hidden])'),panel=slide?.querySelector('.micro-flow');if(!panel){stop();active=null;return;}activate(panel,true);}
  document.querySelectorAll('.slide').forEach(slide=>{const type=slide.dataset.flow||mapping[slide.id];if(type&&flows[type])build(slide,type);});
  window.addEventListener('lesson:slidechange',enter);document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});motion.addEventListener('change',()=>{if(motion.matches)stop();});
  const proof=document.getElementById('scaling-proof');
  document.addEventListener('click',event=>{if(event.target.closest('[data-open-scaling-proof]')){stop();proof?.showModal();}if(event.target.closest('[data-close-proof]'))proof?.close();});
  document.getElementById('open-toc')?.addEventListener('click',stop);
  let printDetails=[];
  window.addEventListener('beforeprint',()=>{stop();if(printDetails.length)return;printDetails=Array.from(document.querySelectorAll('details.review')).map(element=>({element,open:element.open,name:element.getAttribute('name')}));printDetails.forEach(({element})=>{element.removeAttribute('name');element.open=true;});});
  window.addEventListener('afterprint',()=>{const snapshot=printDetails;printDetails=[];snapshot.forEach(({element})=>element.open=false);snapshot.forEach(({element,open,name})=>{if(name!==null)element.setAttribute('name',name);element.open=open;});});
  enter();
})();
