# Python 抽象类与默认实现详解

## 1. 核心问题的答案

**Q: Python 的抽象类里的抽象方法可以带默认实现吗？**
**A: 可以。**

在 Python 的 `abc` 模块中，`@abstractmethod` 装饰的方法完全可以包含代码实现。

但这有一个重要的行为特性：**即使父类提供了默认实现，子类仍然被强制要求重写该方法。** 子类可以在重写时通过 `super()` 来调用父类的默认实现。

## 2. 代码示例

### 2.1 基础写法

```python
from abc import ABC, abstractmethod

class BaseService(ABC):
    
    @abstractmethod
    def connect(self):
        """这是一个抽象方法，但它包含通用的连接逻辑"""
        print("[Base] 正在初始化通用连接参数...")
        # 假设这里有一些所有子类都需要的公共逻辑
        self.connected = True

class MySQLService(BaseService):
    def connect(self):
        # 1. 必须重写，否则报错
        # 2. 可以调用父类的默认实现（复用逻辑）
        super().connect() 
        print("[MySQL] 正在进行 MySQL 特有的握手...")

# 使用
service = MySQLService()
service.connect()
# 输出:
# [Base] 正在初始化通用连接参数...
# [MySQL] 正在进行 MySQL 特有的握手...
```

### 2.2 如果子类不重写会怎样？

```python
class RedisService(BaseService):
    pass 
    # 没有重写 connect

# r = RedisService() 
# 报错: TypeError: Can't instantiate abstract class RedisService with abstract method connect
```

这证明了：即使父类有实现，`@abstractmethod` 依然起到了“强制子类必须有自己的实现”的契约作用。

---

## 3. 为什么要这么设计？ (设计模式)

这种模式通常被称为 **"模板方法模式" (Template Method Pattern)** 的变体或钩子方法。

*   **强制契约**：保证子类必须显式地处理这个方法（不能忘记）。
*   **代码复用**：父类提供通用的基础逻辑，子类决定是否使用它。

如果你希望子类**可选**重写（即子类不写就直接用父类的），那么**不要**加 `@abstractmethod` 装饰器，直接写成普通方法即可。

## 4. 与 Java 的对比

| 特性 | Python Abstract Class | Java Abstract Class | Java Interface (Default Methods) |
| :--- | :--- | :--- | :--- |
| **抽象方法带实现** | ✅ 支持 | ❌ 不支持 (Java 抽象方法不能有体) | ✅ 支持 (default 关键字) |
| **强制重写** | ✅ 即使有实现也必须重写 | ✅ 必须重写 | ❌ 不强制 (可直接继承使用) |
| **调用父类实现** | `super().method()` | 无法调用 (因为没体) | `InterfaceName.super.method()` |

### Java 写法对比

**Java:**
```java
abstract class Base {
    // 只能定义签名，不能写实现
    abstract void connect(); 
    
    // 如果要有实现，必须是普通方法
    void commonConnect() { ... }
}
```

**Python:**
```python
class Base(ABC):
    # 既是抽象的（强制重写），又有实现（提供复用）
    @abstractmethod
    def connect(self):
        print("common logic")
```
