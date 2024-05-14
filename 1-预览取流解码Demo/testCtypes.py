from ctypes import *

# 定义一个外部C函数
# 假设我们有一个C库的函数，名为`add`，它接受两个指向整数的指针，并将结果存储在第一个指针指向的位置
# extern void add(int *a, int *b);

# 加载这个假设的C库
# libc = CDLL('path_to_your_c_library')

# 这里我们模拟这个过程，假设这个函数的实现如下
def add(a_ptr, b_ptr):
    # 通过a_ptr.contents.value访问指针指向的值
    a_ptr.contents.value += b_ptr.contents.value

# 使用ctypes定义与C函数匹配的参数类型
# 假设`add`函数已经按照上述方式加载并绑定
# libc.add.argtypes = [POINTER(c_int), POINTER(c_int)]

# 创建两个整数变量
a = c_int(5)
b = c_int(3)

# 调用函数，使用byref获取变量的引用
# libc.add(byref(a), byref(b))
add(byref(a), byref(b))  # 使用模拟的Python函数替代

# 检查结果
print(a.value)  # 输出应该是8，因为5+3=8
