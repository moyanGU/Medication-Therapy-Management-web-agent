// slide-06.js - 总结与展望页
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'summary',
  index: 6,
  title: '总结'
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.primary };
  
  // 装饰圆形
  slide.addShape(pres.shapes.OVAL, {
    x: -1, y: -1, w: 3, h: 3,
    fill: { color: theme.secondary, transparency: 60 }
  });
  
  slide.addShape(pres.shapes.OVAL, {
    x: 8.5, y: 4, w: 2.5, h: 2.5,
    fill: { color: theme.accent, transparency: 50 }
  });
  
  // 标题
  slide.addText("项目总结", {
    x: 0.5, y: 0.5, w: 9, h: 0.7,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: "FFFFFF", bold: true,
    align: "center"
  });
  
  // 核心价值
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 1.4, w: 9, h: 1.6,
    fill: { color: "FFFFFF", transparency: 15 },
    rectRadius: 0.15
  });
  
  slide.addText("🎯 核心价值", {
    x: 0.7, y: 1.5, w: 8.6, h: 0.4,
    fontSize: 16, fontFace: "Microsoft YaHei",
    color: theme.light, bold: true
  });
  
  slide.addText("MTM-用药助手致力于解决老年人用药管理难题，通过AI智能、适老化设计、多渠道提醒等功能，提升用药依从性，降低用药风险，守护老年人健康。", {
    x: 0.7, y: 1.95, w: 8.6, h: 0.9,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: "FFFFFF",
    lineSpaceMult: 1.5
  });
  
  // 数据亮点
  const stats = [
    { value: "4+", label: "核心功能模块" },
    { value: "AI+", label: "智能用药咨询" },
    { value: "3+", label: "提醒推送渠道" }
  ];
  
  stats.forEach((stat, index) => {
    const xPos = 0.8 + index * 3.1;
    
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: xPos, y: 3.2, w: 2.8, h: 1.0,
      fill: { color: "FFFFFF" },
      rectRadius: 0.1
    });
    
    slide.addText(stat.value, {
      x: xPos, y: 3.28, w: 2.8, h: 0.5,
      fontSize: 28, fontFace: "Microsoft YaHei",
      color: theme.primary, bold: true,
      align: "center"
    });
    
    slide.addText(stat.label, {
      x: xPos, y: 3.78, w: 2.8, h: 0.35,
      fontSize: 12, fontFace: "Microsoft YaHei",
      color: theme.secondary,
      align: "center"
    });
  });
  
  // 底部标语
  slide.addText("感谢聆听 · 期待支持", {
    x: 0.5, y: 4.5, w: 9, h: 0.5,
    fontSize: 20, fontFace: "Microsoft YaHei",
    color: theme.light, bold: true,
    align: "center"
  });
  
  slide.addText("药学创新大赛 · 第19号作品", {
    x: 0.5, y: 5.0, w: 9, h: 0.35,
    fontSize: 12, fontFace: "Microsoft YaHei",
    color: theme.secondary,
    align: "center"
  });
  
  return slide;
}

if (require.main === module) {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  const theme = {
    primary: "006d77",
    secondary: "83c5be",
    accent: "e29578",
    light: "ffddd2",
    bg: "edf6f9"
  };
  createSlide(pres, theme);
  pres.writeFile({ fileName: "slide-06-preview.pptx" });
}

module.exports = { createSlide, slideConfig };
