# 贸泽电子元器件价格爬虫 - Web版本

这是一个将原有的桌面应用程序改造为Web应用程序的版本，用户可以通过浏览器在线使用该工具查询贸泽电子元器件的价格信息。

## 功能特点

- 通过Web界面查询单个或批量电子元器件价格
- 支持Excel和TXT文件导入元件型号
- 可下载Excel模板文件
- 查询结果可导出为Excel文件
- 用户需要提供自己的Mouser API密钥

## 部署说明

### 免费部署平台推荐

1. **Railway** (推荐) - 简单易用，免费额度充足
2. **Vercel** - 支持Python后端部署
3. **Render** - 另一个Heroku的优秀替代品

### 本地运行

1. 安装依赖:
   ```
   pip install -r requirements.txt
   ```

2. 启动应用:
   ```
   python main.py
   ```

3. 在浏览器中访问 `http://localhost:5000`

### Railway部署步骤

1. 注册[Railway](https://railway.app/)账户
2. 在Railway控制台创建新项目
3. 连接你的Git仓库或直接上传代码
4. Railway会自动检测这是Python应用并创建服务
5. 部署完成后，Railway会提供一个公共URL访问你的应用

### Vercel部署步骤

1. 注册[Vercel](https://vercel.com/)账户
2. 安装Vercel CLI: `npm install -g vercel`
3. 在项目根目录运行: `vercel --prod`
4. 按照提示完成部署

## 使用说明

1. 访问应用首页
2. 在API密钥输入框中输入你的Mouser API密钥
3. 选择以下方式之一输入元件型号:
   - 在单个元件输入框中输入型号
   - 在批量输入框中每行输入一个型号
   - 上传包含元件型号的Excel或TXT文件
4. 点击"搜索价格"按钮开始查询
5. 查询完成后可导出结果到Excel文件

## API密钥获取

1. 访问[Mouser API官网](https://www.mouser.com/api-hub/)
2. 注册账户并申请API密钥
3. 将获得的API密钥输入到应用中使用

## 技术栈

- Python 3.x
- Flask (Web框架)
- requests (HTTP请求)
- openpyxl (Excel处理)
- pandas (数据处理)
- Bootstrap 5 (前端框架)
- jQuery (前端交互)