"""Embed offline microscope diagrams and the scaling proof into the stable review deck."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / 'docs' / 'lessons'
ASSETS = LESSONS / 'interactive'


def main():
    path = LESSONS / 'transformer-slides.html'
    source = path.read_text(encoding='utf-8')
    source = re.sub(r'\n?<!-- COURSE_FLOW_CSS -->[\s\S]*?<!-- END_COURSE_FLOW_CSS -->\n?', '', source)
    source = re.sub(r'\n?<!-- COURSE_FLOW_RUNTIME -->[\s\S]*?<!-- END_COURSE_FLOW_RUNTIME -->\n?', '', source)
    css = '\n<!-- COURSE_FLOW_CSS -->\n<style>\n' + (ASSETS / 'flow.css').read_text(encoding='utf-8') + '\n</style>\n<!-- END_COURSE_FLOW_CSS -->\n'
    source = source.replace('</head>', css + '</head>', 1)
    runtime = '\n<!-- COURSE_FLOW_RUNTIME -->\n' + (ASSETS / 'scaling-proof.html').read_text(encoding='utf-8') + '\n<script>\n' + (ASSETS / 'flow.js').read_text(encoding='utf-8') + '\n</script>\n<!-- END_COURSE_FLOW_RUNTIME -->\n'
    source = source.replace('</body>', runtime + '</body>', 1)
    hook = "    window.scrollTo({top:0,behavior:'instant'});"
    if "new CustomEvent('lesson:slidechange'" not in source:
        assert source.count(hook) == 1
        source = source.replace(hook, hook + "\n    window.dispatchEvent(new CustomEvent('lesson:slidechange',{detail:{id:slides[index].id}}));")
    source = source.replace("if(toc.open||event.altKey", "if(document.querySelector('dialog[open]')||event.altKey")
    old = '<p>在常用统计假设下，点积的典型尺度随维度增长；这个系数补偿相应的尺度变化。</p>'
    new = '<p>在下述简化假设下，点积方差为 dₖ，标准差为 √dₖ；除以它后，方差回到 1。</p><button class="proof-trigger" type="button" data-open-scaling-proof>展开假设、公式与完整推导</button>'
    if old in source:
        source = source.replace(old, new, 1)
    assert 'data-open-scaling-proof' in source
    path.write_text(source, encoding='utf-8')
    print('Embedded microscope flows and scaling derivation; preserved slide ids and ordering.')


if __name__ == '__main__':
    main()
