# GitHub 部署说明

公开阅读版：../virus-atlas/

完整网站：https://virus-atlas-bilingual-20261120.wangyidan-yd.chatgpt.site

GitHub Pages 只提供资料快照。审核登录、Zotero 同步、服务端权限验证、R2 存储及每日更新继续运行在完整网站。不能将后台脚本当作静态文件部署来替代服务端授权。

源码不包含运行时密钥、Zotero 账号配置、私人文献或审核数据。源码中的 .openai/hosting.json 是无项目身份的模板，部署独立 Worker 前需配置自己的平台、存储与可信登录入口。

构建：Node 22+，运行 node scripts/build-worker.mjs。GitHub Pages 不运行此 Worker。
