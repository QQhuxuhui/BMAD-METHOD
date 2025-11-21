const pptxgen = require('pptxgenjs');
const html2pptx = require('/root/.claude/plugins/marketplaces/anthropic-agent-skills/document-skills/pptx/scripts/html2pptx.js');
const path = require('path');

async function createPresentation() {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.author = 'APS团队';
  pptx.title = 'APS调度智能体系统 - 价值汇报';

  // 创建唯一的一页PPT
  const htmlFile = path.join(__dirname, 'aps-value-slide.html');
  const { slide, placeholders } = await html2pptx(htmlFile, pptx);

  // 保存PPT
  const outputFile = path.join(__dirname, 'APS产品价值汇报-一页版.pptx');
  await pptx.writeFile({ fileName: outputFile });
  console.log(`PPT创建成功: ${outputFile}`);
}

createPresentation().catch((err) => {
  console.error('创建PPT时出错:', err);
  process.exit(1);
});
