# ⚡ 快速开始

## 🎯 最快方式（30秒）

### Mac/Linux
```bash
cd visualization_dashboard
./start_local.sh
```

### Windows
双击 `start_local.bat`

### 手动启动
```bash
cd visualization_dashboard
python3 -m http.server 8000
```

然后在浏览器打开：**http://localhost:8000**

---

## 🌐 在线部署（5分钟）

### 方案A：Netlify（最简单）
1. 访问 [netlify.com](https://app.netlify.com)
2. 拖拽 `visualization_dashboard` 文件夹
3. 完成！获得 `xxx.netlify.app` 链接

### 方案B：Vercel（推荐）
1. 访问 [vercel.com](https://vercel.com)
2. 导入项目或上传文件夹
3. 完成！获得 `xxx.vercel.app` 链接

### 方案C：GitHub Pages
1. 创建 GitHub 仓库
2. 上传文件
3. Settings → Pages → 选择 main 分支
4. 完成！获得 `用户名.github.io/仓库名` 链接

---

## 📋 部署前准备

确保以下文件存在：
- ✅ `index.html`
- ✅ `styles.css`
- ✅ `dashboard.js`
- ✅ `data.js`（数据文件）

---

## 🔄 更新数据

```bash
cd visualization_dashboard
python3 update_data.py
```

然后重新部署即可。

---

详细说明请查看 [DEPLOY.md](./DEPLOY.md)

