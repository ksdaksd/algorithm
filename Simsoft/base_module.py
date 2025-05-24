class BaseModule(ttk.Frame):
    """各功能模块页面的基类，提供统一的布局结构"""

    def __init__(self, parent, controller):
        super().__init__(parent, style="TFrame")  # 基础Frame使用主题样式
        # 主内容区（卡片内容），在子类中向其中添加控件
        # self.content = ttk.Frame(self, style="Card.TFrame")  # Card.TFrame 自定义样式
        # self.content.pack(fill="both", expand=True, padx=15, pady=10)
        # ↑ 给 content Frame 设置较浅背景和圆角边框，以实现卡片视觉效果
        #   可通过 Style.configure("Card.TFrame", borderwidth=1, relief="solid", bordercolor=...) 来定制边框:contentReference[oaicite:8]{index=8}

        # 底部导航工具栏（返回主菜单、查看报告等按钮）
        toolbar = ttk.Frame(self)
        toolbar.pack(side="bottom", fill="x", pady=5)
        ttk.Button(toolbar, text="返回主菜单", bootstyle="secondary-outline",
                   command=lambda: controller.show_frame(MainMenu)
                   ).pack(side="left", padx=5)
        ttk.Button(toolbar, text="查看报告", bootstyle="secondary-outline",
                   command=lambda: controller.show_frame(ReportView)
                   ).pack(side="right", padx=5)
        # ↑ 使用 bootstyle="secondary-outline" 创建浅色圆角边框按钮:contentReference[oaicite:9]{index=9}，悬停时会高亮，风格统一