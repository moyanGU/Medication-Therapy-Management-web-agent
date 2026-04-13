// compile.js - 编译所有幻灯片为最终PPT
const pptxgen = require('pptxgenjs');
const pres = new pptxgen();

// 设置幻灯片尺寸
pres.layout = 'LAYOUT_16x9';

// 设置PPT元数据
pres.title = 'MTM-用药助手 - 药学创新大赛参赛作品';
pres.subject = '智能药品管理系统';
pres.author = 'MTM团队';

// Modern & Wellness 配色方案
const theme = {
  primary: "006d77",    // 深青色 - 标题/主色
  secondary: "83c5be",  // 浅青色 - 次要元素
  accent: "e29578",      // 珊瑚色 - 强调
  light: "ffddd2",       // 浅粉色 - 辅助
  bg: "edf6f9"          // 极浅蓝 - 背景
};

// 按顺序加载并创建所有幻灯片
for (let i = 1; i <= 6; i++) {
  const num = String(i).padStart(2, '0');
  const slideModule = require(`./slide-${num}.js`);
  slideModule.createSlide(pres, theme);
  console.log(`✓ Slide ${num} added`);
}

// 输出最终PPT
pres.writeFile({ fileName: './output/MTM用药助手-参赛PPT.pptx' })
  .then(fileName => {
    console.log(`\n✅ PPT生成成功: ${fileName}`);
  })
  .catch(err => {
    console.error('❌ PPT生成失败:', err);
  });
