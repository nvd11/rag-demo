# Python 抽象属性 (@property + @abstractmethod) 详解

本文档详细解释了为什么在 Python 中会将 `@property` 和 `@abstractmethod` 结合使用，以及子类应该如何实现它。

## 1. 为什么要组合使用？

在 `BaseLoader` 代码中：

```python
@property
@abstractmethod
def supported_extensions(self) -> list[str]:
    """Return list of supported file extensions."""
    pass
```

这种写法的核心目的是：**定义一个只读的、强制子类提供的数据接口。**

### 1.1 语义区别
*   **方法 (Method)**: 表示“动作”或“计算”。调用需要括号 `()`。
*   **属性 (Property)**: 表示“状态”、“特征”或“配置”。调用不需要括号。

`supported_extensions` 本质上是 Loader 的一种**静态特征**（它支持什么后缀），而不是一个动作（比如 `load()`）。因此，将其定义为属性在语义上更准确。

---

## 2. 子类如何实现？

这是这种模式最强大的地方：**它给了子类极大的灵活度。**

父类定义了“我需要一个名为 `supported_extensions` 的属性”，子类可以用以下两种方式之一来满足：

### 方式一：使用属性 (最简单推荐)
这也是 Python 相比 Java 的一大优势：**抽象属性可以用普通的类属性或实例属性来覆盖。**

```python
class TextLoader(BaseLoader):
    # 直接定义一个列表，甚至不需要写 @property 方法
    supported_extensions = ['.txt', '.md']
```

这种写法非常干净，看起来就像是在写配置文件。

### 方式二：使用 @property 方法 (动态计算)
如果你的属性值不是固定的，而是需要计算得来的，可以使用这种方式。

```python
class DynamicLoader(BaseLoader):
    @property
    def supported_extensions(self) -> list[str]:
        # 假设这里有复杂的逻辑
        import os
        return os.environ.get("ALLOWED_EXTS", ".txt").split(",")
```

---

## 3. 完整示例对比

```python
from abc import ABC, abstractmethod

class Base(ABC):
    @property
    @abstractmethod
    def config(self):
        pass

# 实现 1: 静态配置 (推荐)
class SimpleImpl(Base):
    config = {"timeout": 30}

# 实现 2: 动态逻辑
class ComplexImpl(Base):
    @property
    def config(self):
        return {"timeout": self._calculate_timeout()}

    def _calculate_timeout(self):
        return 100

# 使用
s = SimpleImpl()
print(s.config) # {'timeout': 30}

c = ComplexImpl()
print(c.config) # {'timeout': 100}
```

## 4. 总结

使用 `@property` + `@abstractmethod` 的好处：
1.  **接口语义清晰**：告诉使用者这是一个数据特征。
2.  **实现灵活**：子类可以简单地用变量赋值，也可以用复杂的 getter 方法。
3.  **统一调用**：无论子类怎么实现，使用者都用 `obj.field` 来访问，不需要关心背后是变量还是函数。
