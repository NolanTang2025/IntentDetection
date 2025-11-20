# 快速部署指南

这是一个纯静态的HTML/CSS/JavaScript项目，可以通过多种方式快速部署。

## 🚀 方法一：本地快速预览（最简单）

### 使用Python（推荐）

```bash
# 进入项目目录
cd visualization_dashboard

# Python 3
python3 -m http.server 8000

# 或者 Python 2
python -m SimpleHTTPServer 8000
```

然后在浏览器打开：`http://localhost:8000`

### 使用Node.js

```bash
# 安装 http-server（如果还没有）
npm install -g http-server

# 启动服务器
cd visualization_dashboard
http-server -p 8000
```

### 使用PHP

```bash
cd visualization_dashboard
php -S localhost:8000
```

---

## 🌐 方法二：GitHub Pages（免费，适合公开演示）

### 步骤：

1. **创建GitHub仓库**
   ```bash
   cd visualization_dashboard
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **推送到GitHub**
   ```bash
   # 在GitHub上创建新仓库，然后：
   git remote add origin https://github.com/你的用户名/你的仓库名.git
   git branch -M main
   git push -u origin main
   ```

3. **启用GitHub Pages**
   - 进入仓库 Settings → Pages
   - Source 选择 `main` 分支
   - 点击 Save
   - 几分钟后访问：`https://你的用户名.github.io/你的仓库名/`

---

## 📦 方法三：Netlify（拖拽部署，最简单）

### 步骤：

1. **访问** [https://app.netlify.com](https://app.netlify.com)

2. **拖拽部署**
   - 直接将 `visualization_dashboard` 文件夹拖到 Netlify 的部署区域
   - 或者点击 "Add new site" → "Deploy manually"

3. **完成**
   - 几秒钟后获得一个 `https://xxx.netlify.app` 的链接
   - 可以自定义域名

### 使用Netlify CLI（可选）

```bash
# 安装Netlify CLI
npm install -g netlify-cli

# 登录
netlify login

# 部署
cd visualization_dashboard
netlify deploy

# 生产环境部署
netlify deploy --prod
```

---

## ⚡ 方法四：Vercel（快速，适合演示）

### 步骤：

1. **访问** [https://vercel.com](https://vercel.com)

2. **导入项目**
   - 点击 "New Project"
   - 连接 GitHub 仓库或直接上传文件夹
   - Framework Preset 选择 "Other"
   - Root Directory 设置为 `visualization_dashboard`

3. **部署**
   - 点击 Deploy
   - 几秒钟后获得 `https://xxx.vercel.app` 链接

### 使用Vercel CLI（可选）

```bash
# 安装Vercel CLI
npm install -g vercel

# 部署
cd visualization_dashboard
vercel

# 生产环境部署
vercel --prod
```

---

## 🔧 方法五：其他静态托管服务

### Surge.sh

```bash
# 安装
npm install -g surge

# 部署
cd visualization_dashboard
surge

# 首次使用需要注册账号
# 会获得 xxx.surge.sh 的链接
```

### Cloudflare Pages

1. 访问 [Cloudflare Pages](https://pages.cloudflare.com)
2. 连接 GitHub 仓库或直接上传
3. 构建命令留空（纯静态项目）
4. 输出目录：`visualization_dashboard`

---

## 📝 部署前检查清单

- [ ] 确保 `data.js` 文件存在且包含最新数据
- [ ] 检查 `index.html` 中的外部资源链接（Chart.js CDN）是否正常
- [ ] 测试所有页面功能是否正常
- [ ] 检查响应式设计在不同设备上的表现

---

## 🔄 更新数据后重新部署

如果数据更新了，需要：

1. **更新数据文件**
   ```bash
   cd visualization_dashboard
   python3 update_data.py
   ```

2. **重新部署**
   - GitHub Pages：推送新的 `data.js` 到仓库
   - Netlify/Vercel：重新拖拽或推送代码

---

## 💡 推荐方案

- **本地演示**：使用方法一（Python http.server）
- **公开演示**：推荐 Netlify（最简单）或 Vercel（速度快）
- **长期项目**：GitHub Pages（免费且稳定）

---

## 🆘 常见问题

### 1. 页面空白？
- 检查浏览器控制台是否有错误
- 确认 `data.js` 文件存在且格式正确
- 检查网络连接（Chart.js 从 CDN 加载）

### 2. 图表不显示？
- 检查 Chart.js CDN 链接是否可访问
- 查看浏览器控制台的网络请求

### 3. 数据不更新？
- 运行 `update_data.py` 更新 `data.js`
- 清除浏览器缓存后刷新

---

## 📞 需要帮助？

如有问题，请检查：
- 浏览器控制台错误信息
- 网络请求状态
- 文件路径是否正确

