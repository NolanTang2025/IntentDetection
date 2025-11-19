# 实时意图生成系统 | Intent Recognition Platform

基于AI技术的智能意图识别系统，通过实时分析用户行为，生成精准的购物意图画像，为Shopify独立站提供个性化的shoppable video体验。

## 功能特性

- 📊 **意图识别框架** - 四层意图识别架构详解
- ⚡ **实时意图体验** - 交互式意图生成演示
- 🎯 **转化链路可视化** - 实时展示用户转化阶段
- 📈 **数据可视化** - 行为统计、参与度分析等图表

## 快速开始

### 本地运行

直接在浏览器中打开 `index.html` 即可。

### 部署到 Vercel

#### 方法一：使用 Vercel CLI（最快）

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录
vercel login

# 部署
vercel

# 生产环境部署
vercel --prod
```

#### 方法二：通过 GitHub

1. 将代码推送到 GitHub
2. 访问 [vercel.com](https://vercel.com)
3. 使用 GitHub 账号登录
4. 导入仓库并自动部署

## 项目结构

```
意图生成介绍/
├── index.html                    # 首页
├── user_intent_report.html        # 意图识别框架页面
├── intent_interactive_demo.html  # 实时意图体验页面
├── products/                      # 产品图片目录
│   ├── hoodie.jpg
│   ├── sweater.jpg
│   ├── pants.jpg
│   ├── jacket.jpg
│   ├── shirt.jpg
│   ├── shoes.jpg
│   ├── banner-comfort.jpg
│   └── banner-style.jpg
├── vercel.json                    # Vercel 配置文件
└── README.md                      # 项目说明
```

## 技术栈

- 纯 HTML/CSS/JavaScript
- 响应式设计
- CSS 动画
- 实时数据可视化

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 许可证

MIT License

