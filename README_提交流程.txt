Titanic Kaggle 作业提交流程
===========================

你现在已经有这几个文件：
1. Titanic_研究报告.md
2. titanic_kaggle_code.py
3. README_提交流程.txt

一、在 Kaggle Notebook 中运行代码
------------------------------
1. 登录 https://www.kaggle.com/
2. 打开 Titanic 比赛页面：
   https://www.kaggle.com/competitions/titanic
3. 新建一个 Notebook
4. 把 titanic_kaggle_code.py 的内容复制进去运行
5. 运行完成后会生成 submission.csv

二、提交预测结果
----------------
1. 在 Titanic 比赛页面点击 Submit Predictions
2. 上传生成的 submission.csv
3. 等待 Kaggle 显示本次提交得分
4. 进入 leaderboard 页面查看排名

三、截图要求
------------
请截一张 leaderboard 截图，最好包含：
- Titanic 比赛名称
- 你的提交分数（score）
- 你的排名（rank）或所在位置

四、补全研究报告
----------------
拿到 Kaggle 结果后，把下面内容补到 Titanic_研究报告.md：
- Kaggle Score
- Leaderboard 排名
- 排名截图
- 简单结果说明（例如：模型得分优于基础模型，说明特征工程和集成模型有效）

五、如果你想继续完善
--------------------
你还可以进一步优化：
- 尝试 XGBoost / LightGBM / CatBoost
- 做更细的参数调优
- 增加 Ticket 相关特征
- 比较不同模型的交叉验证分数
- 在报告中加入可视化图表

六、建议的最终交付材料
----------------------
建议最终提交：
1. 研究报告（可转成 Word/PDF）
2. 核心代码文件
3. leaderboard 截图
4. 提交结果说明
