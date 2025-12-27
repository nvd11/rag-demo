# Python 泛型 (Generics) 详解指南

本文档详细介绍了 Python 泛型的用法，并通过大量代码示例展示如何在 Python 中使用泛型进行类型安全编程。同时，我们也会对比 Java 的泛型机制，帮助你更好地理解两者的区别。

## 1. 为什么需要泛型？

Python 是一门动态语言，但在大型项目中，为了提高代码的可维护性和减少 Bug，我们通常会使用**类型提示 (Type Hints)**。泛型允许我们在定义函数、类或接口时，不指定具体的数据类型，而是在使用时再指定。

**主要好处：**
*   **类型安全**：静态类型检查器（如 `mypy`）可以在运行前发现类型错误。
*   **代码复用**：一套逻辑可以应用于多种数据类型。
*   **IDE 智能提示**：更好的自动补全和代码导航。

---

## 2. 基础概念与语法

### 2.1 定义类型变量 (TypeVar)

在 Python 中（3.12 之前），泛型的核心是 `TypeVar`。必须先定义一个类型变量对象，才能在后续代码中使用它。

```python
from typing import TypeVar, List

# 定义一个类型变量 T
# 习惯上变量名和字符串参数保持一致
T = TypeVar('T')
```

### 2.2 泛型函数

一个简单的例子：实现一个函数，返回列表中的第一个元素。

```python
from typing import TypeVar, List

T = TypeVar('T')

def get_first(items: List[T]) -> T:
    """返回列表的第一个元素，类型与列表元素类型一致"""
    return items[0]

# 使用示例
n: int = get_first([1, 2, 3])      # T 被推断为 int
s: str = get_first(["a", "b"])     # T 被推断为 str

# IDE 会报错的例子:
# x: str = get_first([1, 2, 3])    # 错误: 期望返回 int，但标记为 str
```

### 2.3 泛型类

使用 `Generic[T]` 基类来定义泛型类。这在你的 `BaseLoader` 代码中已经见过。

```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()

# 具体化使用
int_stack = Stack[int]()
int_stack.push(1)
# int_stack.push("a")  # 类型检查错误: 期望 int

str_stack = Stack[str]()
str_stack.push("hello")
```

### 2.4 多个类型变量

类似于 Java 的 `Map<K, V>`。

```python
K = TypeVar('K')
V = TypeVar('V')

class KeyValuePair(Generic[K, V]):
    def __init__(self, key: K, value: V):
        self.key = key
        self.value = value

pair = KeyValuePair[str, int]("age", 25)
```

### 2.5 上界约束 (Bound)

有时我们需要限制 T 必须是某个类的子类。

```python
class Animal:
    def speak(self): pass

class Dog(Animal): ...
class Cat(Animal): ...

# T 必须是 Animal 或其子类
A = TypeVar('A', bound=Animal)

def make_noise(animal: A) -> None:
    animal.speak()

make_noise(Dog()) # OK
# make_noise("hello") # Error: str 不是 Animal 的子类
```

---

## 3. Python vs Java 泛型对比

这是最关键的部分，理解两者的差异有助于你从 Java 思维转换到 Python 思维。

### 3.1 语法对比

| 特性 | Java | Python (3.5 - 3.11) | Python (3.12+) |
| :--- | :--- | :--- | :--- |
| **定义泛型类** | `class Box<T> { ... }` | `class Box(Generic[T]): ...` | `class Box[T]: ...` |
| **定义泛型方法** | `public <T> T func(T x)` | `def func(x: T) -> T:` | `def func[T](x: T) -> T:` |
| **类型变量声明** | 隐式声明 (直接写 `<T>`) | **必须显式声明** (`T = TypeVar('T')`) | 隐式声明 (3.12+ 新语法) |
| **实例化** | `new Box<Integer>()` | `Box[int]()` | `Box[int]()` |
| **通配符** | `List<?>` | `List[Any]` | `List[Any]` |
| **上界约束** | `<T extends Number>` | `TypeVar('T', bound=Number)` | `class Box[T: Number]:` |

### 3.2 核心机制差异

#### Java: 伪泛型与类型擦除 (Type Erasure)
*   **机制**：Java 编译器在编译时检查类型，但在生成的字节码中，所有的 `T` 都会被替换成 `Object` (或其他上界)。运行时 JVM 不知道 `List<String>` 和 `List<Integer>` 的区别。
*   **后果**：你不能在运行时做 `if (obj instanceof T)` 这样的检查。

#### Python: 运行时对象与静态检查
*   **机制**：Python 是动态的。`Generic[T]` 和 `TypeVar('T')` 都是**运行时的真实对象**。
*   **检查**：Python 解释器本身**完全忽略**这些类型提示，不会在运行时报错（除非代码逻辑本身错了）。类型检查完全依赖外部工具（如 `mypy`, `pyright`, 或 IDE）。
*   **后果**：你可以运行 `x: int = "hello"`，Python 解释器照样执行不误。必须配合 `mypy` 使用才有意义。

### 3.3 代码直接对比

**Java:**
```java
// Java 不需要提前定义 T
public class Box<T> {
    private T content;
    
    public void set(T content) {
        this.content = content;
    }
    
    public T get() {
        return content;
    }
}

// 使用
Box<String> box = new Box<>();
box.set("hello");
```

**Python:**
```python
from typing import TypeVar, Generic

# Python 必须先定义 T
T = TypeVar('T') 

class Box(Generic[T]):
    def __init__(self) -> None:
        self.content: T = None
        
    def set(self, content: T) -> None:
        self.content = content
        
    def get(self) -> T:
        return self.content

# 使用
box = Box[str]()
box.set("hello")
```

### 3.4 上界约束对比 (Upper Bound)

Java 使用 `extends` 关键字来实现上界约束，而 Python 在 `TypeVar` 定义中使用 `bound` 参数。

**Java:**
```java
// T 必须是 Animal 或其子类
public class Zoo<T extends Animal> {
    private T animal;
    
    public void set(T animal) {
        // 可以安全调用 Animal 的方法
        animal.speak();
    }
}
```

**Python:**
```python
# T 必须是 Animal 或其子类
T = TypeVar('T', bound='Animal')

class Zoo(Generic[T]):
    def __init__(self, animal: T):
        self.animal = animal
        
    def set(self, animal: T) -> None:
        # 可以安全调用 Animal 的方法
        self.animal.speak()
```

---

## 4. 进阶用法示例 (结合你的项目)

在 RAG 系统或数据处理管道中，泛型非常有用。

### 4.1 泛型 Repository 模式

```python
from typing import TypeVar, Generic, List, Optional
from dataclasses import dataclass

# 假设有两个实体模型
@dataclass
class User:
    id: int
    name: str

@dataclass
class Document:
    id: int
    content: str

# 定义泛型 T，约束为必须有 id 属性 (这里用 Protocol 更高级，但简化演示用)
T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self):
        self.db: dict[int, T] = {}

    def save(self, entity: T) -> None:
        # 假设实体都有 id 属性
        self.db[entity.id] = entity

    def get(self, id: int) -> Optional[T]:
        return self.db.get(id)

    def find_all(self) -> List[T]:
        return list(self.db.values())

# 具体实现
class UserRepository(BaseRepository[User]):
    def find_by_name(self, name: str) -> Optional[User]:
        for user in self.db.values():
            if user.name == name:
                return user
        return None

# 使用
user_repo = UserRepository()
user_repo.save(User(1, "Alice"))
user = user_repo.get(1) # 类型自动推断为 User
```

### 4.2 泛型 Protocol (类似 Java Interface)

如果你想定义一个“只要有 `read()` 方法的对象”，不管它继承自谁。

```python
from typing import Protocol, TypeVar

T = TypeVar('T')

class Reader(Protocol[T]):
    def read(self) -> T:
        ...

def process_data(reader: Reader[str]) -> None:
    print(reader.read())

class FileReader:
    def read(self) -> str:
        return "file content"

# FileReader 没有继承 Reader，但符合结构，可以通过检查
process_data(FileReader())
```

---

## 5. 总结

1.  **显式定义**：Python (3.12前) 需要 `T = TypeVar('T')`。
2.  **继承 Generic**：类需要继承 `Generic[T]` 才能成为泛型类。
3.  **工具检查**：泛型主要服务于静态检查工具和 IDE，运行时不会强制校验。
4.  **灵活性**：Python 的泛型系统非常强大，配合 `Protocol` (结构化类型) 可以实现比 Java 更灵活的模式。
