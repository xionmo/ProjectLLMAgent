  function architecture(host){
    const NS='http://www.w3.org/2000/svg',svg=document.createElementNS(NS,'svg');
    svg.setAttribute('viewBox','0 0 650 570');svg.setAttribute('role','group');svg.setAttribute('aria-label','完整 Transformer 架构导航；每个模块可打开对应章节。');
    function element(tag,attrs,parent=svg){const item=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([key,value])=>item.setAttribute(key,String(value)));parent.appendChild(item);return item;}
    function text(x,y,value,size=16,parent=svg){const item=element('text',{x,y,'text-anchor':'middle','dominant-baseline':'middle','font-size':size,fill:'var(--ink)'},parent);item.textContent=value;return item;}
    function wire(path){element('path',{d:path,class:'wire','marker-end':'url(#unit-atlas-arrow)'});}
    const defs=element('defs',{}),marker=element('marker',{id:'unit-atlas-arrow',viewBox:'0 0 8 8',refX:7,refY:4,markerWidth:5,markerHeight:5,orient:'auto'},defs);element('path',{d:'M 0 0 L 8 4 L 0 8 Z',fill:'#72878d'},marker);
    function node(x,y,title,formula,target){const link=element('a',{href:'#'+target,'data-jump':target,'aria-label':'打开 '+title+' 的计算章节'});element('rect',{x:x-108,y:y-23,width:216,height:46,rx:5,class:'node'},link);text(x,y-9,title,16,link);text(x,y+10,formula,15,link);const tip=element('title',{},link);tip.textContent='打开：'+title;}
    text(155,22,'Encoder · N = 6',17);text(485,22,'Decoder · N = 6',17);
    element('rect',{x:29,y:216,width:252,height:226,rx:9,class:'frame'});element('rect',{x:359,y:109,width:252,height:333,rx:9,class:'frame'});
    for(const x of [155,485]){wire('M '+x+' 463 V 433');wire('M '+x+' 387 V 379');wire('M '+x+' 333 V 325');wire('M '+x+' 279 V 271');wire('M '+x+' 445 H '+(x+118)+' V 356 H '+(x+108));wire('M '+x+' 329 H '+(x+118)+' V 248 H '+(x+108));}
    wire('M 485 225 V 217');wire('M 485 171 V 163');wire('M 485 221 H 603 V 140 H 593');wire('M 485 117 V 109');wire('M 485 63 V 59');wire('M 155 225 V 202 H 326 V 302 H 377');text(286,189,'C → K / V',16);
    node(155,248,'Add & Norm','H_next = LN(Y + F)','encoder-second-norm');node(155,302,'Feed Forward','F = FFN(Y)','encoder-ffn');node(155,356,'Add & Norm','Y = LN(H + U)','encoder-attention-addnorm');node(155,410,'Self-Attention','U = MHA(H)','encoder-self-attention');
    node(485,140,'Add & Norm','D = LN(Y₂ + F)','decoder-last-norm');node(485,194,'Feed Forward','F = FFN(Y₂)','decoder-ffn');node(485,248,'Add & Norm','Y₂ = LN(Y₁ + Uc)','decoder-cross-norm');node(485,302,'Cross-Attention','Uc = CrossAttn(Y₁, C)','cross-sources');node(485,356,'Add & Norm','Y₁ = LN(H + Us)','decoder-first-norm');node(485,410,'Masked Self-Attention','Us = MHA_causal(H)','decoder-self-attention');
    node(155,486,'Embedding + 位置','H₀ = √d Embed(x) + P','input-representation');node(485,486,'Embedding + 位置','H₀ = √d Embed(y_shift) + P','decoder-input');node(485,86,'Linear','Z = D W_vocab + b','vocabulary-head');
    const output=element('a',{href:'#softmax-basics','data-jump':'softmax-basics','aria-label':'打开 softmax 计算'});element('rect',{x:377,y:34,width:216,height:25,rx:5,class:'node'},output);text(485,47,'p = softmax_vocab(Z)',16,output);
    text(155,543,'已知源输入',16);text(485,543,'目标序列（右移）',16);wire('M 155 530 V 509');wire('M 485 530 V 509');host.appendChild(svg);
  }
