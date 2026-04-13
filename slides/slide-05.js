// slide-05.js - 技术创新页
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'content',
  index: 5,
  title: '技术创新'
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
  slide.addText("技术创新与安全", {
    x: 0.5, y: 0.3, w: 6, h: 0.55,
    fontSize: 26, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 技术栈展示
  slide.addText("技术架构", {
    x: 0.5, y: 0.95, w: 2, h: 0.35,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: theme.secondary, bold: true
  });
  
  // 技术栈标签
  const techStack = [
    { name: "Vue 3", desc: "前端框架" },
    { name: "Django", desc: "后端框架" },
    { name: "MySQL", desc: "数据库" },
    { name: "Redis", desc: "缓存" },
    { name: "Docker", desc: "容器化" },
    { name: "JWT", desc: "认证" }
  ];
  
  techStack.forEach((tech, index) => {
    const xPos = 0.5 + (index % 6) * 1.55;
    const yPos = 1.35;
    
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: xPos, y: yPos, w: 1.4, h: 0.7,
      fill: { color: theme.primary },
      rectRadius: 0.08
    });
    
    slide.addText(tech.name, {
      x: xPos, y: yPos + 0.08, w: 1.4, h: 0.35,
      fontSize: 12, fontFace: "Microsoft YaHei",
      color: "FFFFFF", bold: true,
      align: "center"
    });
    
    slide.addText(tech.desc, {
      x: xPos, y: yPos + 0.38, w: 1.4, h: 0.25,
      fontSize: 9, fontFace: "Microsoft YaHei",
      color: theme.light,
      align: "center"
    });
  });
  
  // 安全与隐私保护
  slide.addText("安全与隐私", {
    x: 0.5, y: 2.25, w: 2, h: 0.35,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: theme.secondary, bold: true
  });
  
  const securityFeatures = [
    { icon: "🔒", title: "CSP安全策略", desc: "内容安全策略防护XSS攻击" },
    { icon: "🎫", title: "Token黑名单", desc: "JWT令牌安全管理" },
    { icon: "📱", title: "数据加密", desc: "敏感信息加密存储" }
  ];
  
  securityFeatures.forEach((item, index) => {
    const xPos = 0.5 + index * 3.15;
    
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: xPos, y: 2.65, w: 3.0, h: 0.9,
      fill: { color: "FFFFFF" },
      rectRadius: 0.08,
      shadow: { type: "outer", blur: 3, offset: 2, angle: 45, opacity: 0.08 }
    });
    
    slide.addText(`${item.icon} ${item.title}`, {
      x: xPos + 0.15, y: 2.72, w: 2.7, h: 0.35,
      fontSize: 13, fontFace: "Microsoft YaHei",
      color: theme.primary, bold: true
    });
    
    slide.addText(item.desc, {
      x: xPos + 0.15, y: 3.1, w: 2.7, h: 0.35,
      fontSize: 11, fontFace: "Microsoft YaHei",
      color: theme.secondary
    });
  });
  
  // 可扩展性
  slide.addText("可扩展性", {
    x: 0.5, y: 3.75, w: 2, h: 0.35,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: theme.secondary, bold: true
  });
  
  const scalability = [
    { icon: "📦", text: "模块化设计，灵活扩展" },
    { icon: "🔌", text: "Docker一键部署" },
    { icon: "📊", text: "数据可视化报表" },
    { icon: "🌐", text: "支持Web/PWA多端" }
  ];
  
  scalability.forEach((item, index) => {
    const xPos = 0.5 + index * 2.35;
    
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: xPos, y: 4.15, w: 2.2, h: 0.65,
      fill: { color: theme.secondary, transparency: 20 },
      rectRadius: 0.06
    });
    
    slide.addText(`${item.icon} ${item.text}`, {
      x: xPos, y: 4.15, w: 2.2, h: 0.65,
      fontSize: 10, fontFace: "Microsoft YaHei",
      color: theme.primary,
      align: "center", valign: "middle"
    });
  });
  
  // 页码
  slide.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide.addText("5", {
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
  pres.writeFile({ fileName: "slide-05-preview.pptx" });
}

module.exports = { createSlide, slideConfig };
