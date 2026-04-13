// slide-01.js - 封面页（精炼版）
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'cover',
  index: 1,
  title: 'MTM-用药助手'
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // 渐变背景效果用色块模拟
  slide.background = { color: theme.bg };
  
  // 左侧主色块
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 5.5, h: 5.625,
    fill: { color: theme.primary }
  });
  
  // 右上角装饰圆
  slide.addShape(pres.shapes.OVAL, {
    x: 7.5, y: -1.5, w: 4, h: 4,
    fill: { color: theme.secondary, transparency: 40 }
  });
  
  // 右下角装饰圆
  slide.addShape(pres.shapes.OVAL, {
    x: 8, y: 4, w: 3, h: 3,
    fill: { color: theme.accent, transparency: 50 }
  });
  
  // 主标题
  slide.addText("MTM-用药助手", {
    x: 0.5, y: 1.6, w: 5, h: 1.0,
    fontSize: 48, fontFace: "Microsoft YaHei",
    color: "FFFFFF", bold: true
  });
  
  // 副标题
  slide.addText("智能药品管理  守护健康生活", {
    x: 0.5, y: 2.6, w: 5, h: 0.5,
    fontSize: 20, fontFace: "Microsoft YaHei",
    color: theme.light
  });
  
  // 分隔线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.3, w: 2, h: 0.04,
    fill: { color: theme.accent }
  });
  
  // 参赛信息
  slide.addText("药学创新大赛 · 第19号作品", {
    x: 0.5, y: 3.55, w: 4, h: 0.4,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: theme.light
  });
  
  // 右侧标语
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 6.2, y: 2.8, w: 3.0, h: 1.4,
    fill: { color: "FFFFFF" },
    rectRadius: 0.15,
    shadow: { type: "outer", blur: 8, offset: 3, angle: 45, opacity: 0.2 }
  });
  
  slide.addText("👴 老年人\n💊 用药管理\n🤖 AI智能", {
    x: 6.2, y: 2.8, w: 3.0, h: 1.4,
    fontSize: 18, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true,
    align: "center", valign: "middle",
    lineSpaceMult: 1.5
  });
  
  return slide;
}

// Standalone preview
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
  pres.writeFile({ fileName: "slide-01-preview.pptx" });
}

module.exports = { createSlide, slideConfig };
