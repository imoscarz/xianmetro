# 西安地铁路线规划器

基于 PyQt5 和 PyQt-Fluent-Widgets 的西安地铁路线规划应用程序。

## 功能特性

- 🚇 支持输入站名或站点ID进行路线规划
- 📊 提供三种路线规划策略：
  - 最少换乘
  - 最少站点
  - 最短距离
- 🎨 基于 Fluent Design 的现代化界面
- ⚠️ 完善的错误提示和输入验证

## 安装依赖

```bash
pip install PyQt5 PyQt-Fluent-Widgets
```

## 运行应用

```bash
# 在项目根目录下运行
python -m xianmetro.main

# 或直接运行
python xianmetro/main.py
```

## 使用说明

1. **输入起点和终点**：在"起点"和"终点"输入框中输入站名或站点ID
   - 支持站名，如："钟楼"、"小寨"
   - 支持站点ID，如："1422 803|1422 803"

2. **点击"开始规划"按钮**：系统将自动计算三种策略的路线

3. **查看结果**：在三个列表中分别查看不同策略的规划结果
   - 左侧：最少换乘方案
   - 中间：最少站点方案
   - 右侧：最短距离方案

4. **结果格式**：
   ```
   线路名称：站点1 -> 站点2 -> 站点3
   
   总站点数: X
   总距离: X.XX km
   换乘次数: X
   ```

## 项目结构

```
xianmetro/
├── main.py              # 主程序入口
├── ui/
│   ├── __init__.py
│   └── style_ui.py     # UI界面定义
├── core/
│   ├── __init__.py
│   ├── planner.py      # 路线规划算法
│   └── load_graph.py   # 站点数据加载
├── fetch/
│   ├── __init__.py
│   └── fetch_data.py   # 数据获取
└── ...
```

## 注意事项

- 首次运行时，程序会自动从高德地图API获取西安地铁站点数据并保存为 `metro_info.json`
- 如果网络不可用，请确保 `metro_info.json` 文件存在于运行目录中
- 输入的站名或站点ID必须存在于西安地铁线路中，否则会提示错误

## 技术栈

- **UI框架**: PyQt5
- **UI组件库**: PyQt-Fluent-Widgets
- **路线规划**: 基于优先队列的图搜索算法
- **数据来源**: 高德地图API

## 开发者

imoscarz

## 许可证

根据项目的 LICENSE 文件
