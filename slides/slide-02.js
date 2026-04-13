// slide-02.js - 问题背景页（精炼版）
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'content',
  index: 2,
  title: '问题背景'
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };
  
  // 左侧色块
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.12, h: 5.625,
    fill: { color: theme.primary }
  });
  
  // 页面标题
  slide.addText("老龄化社会 · 用药困境", {
    x: 0.5, y: 0.35, w: 5, h: 0.6,
    fontSize: 28, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 数据展示区
  const stats = [
    { value: "2.8亿", label: "60岁以上老年人口", source: "国家统计局" },
    { value: "42%", label: "老年人存在多重用药", source: "世界卫生组织" },
    { value: "50%", label: "依从性差导致治疗失败", source: "临床研究" }
  ];
  
  stats.forEach((stat, index) => {
    const xPos = 0.5 + index * 3.1;
    
    // 卡片背景
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: xPos, y: 1.1, w: 2.9, h: 1.5,
      fill: { color: "FFFFFF" },
      rectRadius: 0.1,
      shadow: { type: "outer", blur: 4, offset: 2, angle: 45, opacity: 0.12 }
    });
    
    // 数值
    slide.addText(stat.value, {
      x: xPos, y: 1.2, w: 2.9, h: 0.7,
      fontSize: 32, fontFace: "Arial",
      color: theme.accent, bold: true,
      align: "center"
    });
    
    // 标签
    slide.addText(stat.label, {
      x: xPos + 0.1, y: 1.9, w: 2.7, h: 0.4,
      fontSize: 11, fontFace: "Microsoft YaHei",
      color: theme.primary, align: "center"
    });
    
    // 来源
    slide.addText(`来源：${stat.source}`, {
      x: xPos + 0.1, y: 2.3, w: 2.7, h: 0.25,
      fontSize: 8, fontFace: "Microsoft YaHei",
      color: theme.secondary, align: "center"
    });
  });
  
  // 痛点标题
  slide.addText("三大核心痛点", {
    x: 0.5, y: 2.85, w: 3, h: 0.45,
    fontSize: 18, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 痛点内容
  const painPoints = [
    { num: "1", title: "忘记服药", desc: "记忆力减退导致漏服错服" },
    { num: "2", title: "药品过期", desc: "药品管理混乱无法及时发现" },
    { num: "3", title: "信息缺失", desc: "缺乏专业用药指导和记录" }
  ];
  
  painPoints.forEach((point, index) => {
    const xPos = 0.5 + index * 3.1;
    const yPos = 3.4;
    
    // 编号圆形
    slide.addShape(pres.shapes.OVAL, {
      x: xPos, y: yPos, w: 0.5, h: 0.5,
      fill: { color: theme.accent }
    });
    slide.addText(point.num, {
      x: xPos, y: yPos, w: 0.5, h: 0.5,
      fontSize: 18, fontFace: "Arial",
      color: "FFFFFF", bold: true,
      align: "center", valign: "middle"
    });
    
    // 标题
    slide.addText(point.title, {
      x: xPos + 0.6, y: yPos + 0.02, w: 2.2, h: 0.35,
      fontSize: 16, fontFace: "Microsoft YaHei",
      color: theme.primary, bold: true
    });
    
    // 描述
    slide.addText(point.desc, {
      x: xPos + 0.6, y: yPos + 0.38, w: 2.2, h: 0.5,
      fontSize: 11, fontFace: "Microsoft YaHei",
      color: theme.secondary
    });
  });
  
  // 底部引用
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.5, w: 9, h: 0.7,
    fill: { color: theme.primary, transparency: 10 }
  });
  
  slide.addText("💡 老年人用药管理问题日益突出，急需智能化解决方案", {
    x: 0.7, y: 4.55, w: 8.6, h: 0.6,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true,
    align: "center", valign: "middle"
  });
  
  // 页码
  slide.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide.addText("2", {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
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
  pres.writeFile({ fileName: "slide-02-preview.pptx" });
}

module.exports = { createSlide, slideConfig };
