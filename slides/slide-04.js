// slide-04.js - 核心功能详解页
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'content',
  index: 4,
  title: '核心功能'
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
  slide.addText("核心功能亮点", {
    x: 0.5, y: 0.3, w: 6, h: 0.55,
    fontSize: 26, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 三大亮点
  const highlights = [
    {
      icon: "🤖",
      title: "AI智能用药咨询",
      points: [
        "百川大模型驱动，智能问答",
        "药品相互作用分析",
        "用药禁忌自动提醒"
      ],
      color: theme.primary
    },
    {
      icon: "👴",
      title: "适老化设计",
      points: [
        "大字体模式（可选32-48px）",
        "语音播报，解放双眼",
        "高对比度色彩方案"
      ],
      color: theme.secondary
    },
    {
      icon: "🔔",
      title: "智能提醒系统",
      points: [
        "微信/短信/APP多渠道推送",
        "餐前/餐中/餐后精准提醒",
        "漏服药物补服建议"
      ],
      color: theme.accent
    }
  ];
  
  highlights.forEach((item, index) => {
    const yPos = 1.0 + index * 1.45;
    
    // 功能卡片
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: yPos, w: 9.2, h: 1.3,
      fill: { color: "FFFFFF" },
      rectRadius: 0.1,
      shadow: { type: "outer", blur: 3, offset: 2, angle: 45, opacity: 0.1 }
    });
    
    // 左侧图标区
    slide.addShape(pres.shapes.OVAL, {
      x: 0.7, y: yPos + 0.25, w: 0.8, h: 0.8,
      fill: { color: item.color, transparency: 20 }
    });
    
    slide.addText(item.icon, {
      x: 0.7, y: yPos + 0.25, w: 0.8, h: 0.8,
      fontSize: 28,
      align: "center", valign: "middle"
    });
    
    // 标题
    slide.addText(item.title, {
      x: 1.7, y: yPos + 0.15, w: 3, h: 0.4,
      fontSize: 18, fontFace: "Microsoft YaHei",
      color: theme.primary, bold: true
    });
    
    // 要点列表
    slide.addText(item.points.join("  ·  "), {
      x: 1.7, y: yPos + 0.55, w: 7.8, h: 0.6,
      fontSize: 12, fontFace: "Microsoft YaHei",
      color: theme.secondary,
      lineSpaceMult: 1.3
    });
  });
  
  // 页码
  slide.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide.addText("4", {
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
  pres.writeFile({ fileName: "slide-04-preview.pptx" });
}

module.exports = { createSlide, slideConfig };
