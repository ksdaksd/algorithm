# import tkinter as tk
#
# root = tk.Tk()
#
# # 创建一个 StringVar
# my_stringvar = tk.StringVar(value="Hello")
#
# # 取值并查看类型
# val = my_stringvar.get()
# print(val, type(val))  # 输出：Hello <class 'str'>
#
# root.mainloop()

class A:
    def b(self):
        self.abc = 1

    def c(self):
        self.b()
        return self.abc

print(A().c())