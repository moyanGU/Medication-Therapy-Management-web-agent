// slide-03.js - 解决方案页（精炼版）
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'content',
  index: 3,
  title: '解决方案'
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
  slide.addText("MTM-用药助手 — 一站式解决方案", {
    x: 0.5, y: 0.35, w: 6, h: 0.6,
    fontSize: 26, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 副标题
  slide.addText("专为老年人设计的智能药品管理系统", {
    x: 0.5, y: 0.9, w: 5, h: 0.35,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: theme.secondary
  });
  
  // 四大功能模块
  const features = [
    {
      icon: "💊",
      title: "药品管理",
      desc: "录入药品信息\n实时监控库存\n过期预警提醒",
      color: theme.primary
    },
    {
      icon: "⏰",
      title: "用药提醒",
      desc: "多频率设置\n餐前餐后提醒\n多渠道推送",
      color: theme.secondary
    },
    {
      icon: "📋",
      title: "服药记录",
      desc: "服药历史追踪\n依从性分析\n效果评估",
      color: theme.accent
    },
    {
      icon: "🏥",
      title: "就医记录",
      desc: "病历存档管理\n医嘱记录\n复诊提醒",
      color: theme.primary
    }
  ];
  
  features.forEach((feature, index) => {
    const xPos = 0.5 + (index % 2) * 4.7;
    const yPos = 1.4 + Math.floor(index / 2) * 2.0;
    
    // 卡片背景
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: xPos, y: yPos, w: 4.4, h: 1.8,
      fill: { color: "FFFFFF" },
      rectRadius: 0.1,
      shadow: { type: "outer", blur: 4, offset: 2, angle: 45, opacity: 0.1 }
    });
    
    // 左侧色条
    slide.addShape(pres.shapes.RECTANGLE, {
      x: xPos, y: yPos, w: 0.1, h: 1.8,
      fill: { color: feature.color }
    });
    
    // 图标和标题行
    slide.addText(`${feature.icon} ${feature.title}`, {
      x: xPos + 0.25, y: yPos + 0.15, w: 4, h: 0.45,
      fontSize: 18, fontFace: "Microsoft YaHei",
      color: theme.primary, bold: true
    });
    
    // 描述
    slide.addText(feature.desc, {
      x: xPos + 0.25, y: yPos + 0.65, w: 4, h: 1.0,
      fontSize: 12, fontFace: "Microsoft YaHei",
      color: theme.secondary,
      lineSpaceMult: 1.4
    });
  });
  
  // 页码
  slide.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide.addText("3", {
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
  pres.writeFile({ fileName: "slide-03-preview.pptx" });
}

module.exports = { createSlide, slideConfig };
