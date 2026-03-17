# 规避加密判断逻辑被发现的技术实践

> 本文仅供技术学习交流，请勿用于非法用途

## 前言

做过软件保护的人都知道：代码混淆只是增加分析成本，真正的核心在于**判断逻辑**——一旦被人定位并理解，破解就只是时间问题。本文探讨如何降低判断逻辑被发现的风险。

---

## 1. 扁平化判断逻辑

### 1.1 分散判断法

把一个完整的判断拆散，藏到多个看似无关的函数里。

**糟糕的做法：**
```javascript
// 一眼就能看出是授权检查
function checkLicense(key) {
    if (!verify(key)) {
        showTrialLimit();
        return false;
    }
    return true;
}
```

**更好的做法：**
```javascript
// 分散成多个独立函数，最后混合结果
function initApp() {
    const a = getHardwareId();      // 获取硬件信息
    const b = loadConfig();         // 加载配置
    const c = calcTimeDelta();      // 计算时间差
    const d = fetchRemoteSeed();   // 远程获取种子
    
    // 关键判断隐藏在混合函数中
    const result = mix(a, b, c, d);  
    // result 为 0 表示验证失败
    if (result === 0) {
        showTrialMode();
    }
}

// mix 函数看起来完全无害
function mix(...args) {
    let sum = 0;
    for (const arg of args) {
        sum ^= (arg * 31337) % 0xFFFFFFFF;
    }
    return sum;
}
```

### 1.2 延迟执行法

判断结果不立即生效，而是延迟几步。

```javascript
// 立即判断
if (!checkAuth()) return;

// 延迟判断：把结果存入变量，后面某处才使用
let authState = null;
function someUnrelatedFunction() {
    authState = checkAuth();
}

// 或者更隐蔽：存到数组/对象里
const appState = { flags: [] };
appState.flags[7] = checkAuth();

// 几千行后...
function deepInTheCode() {
    if (appState.flags[7]) return;  // 被跳过了
    // 功能代码
}
```

### 1.3 状态机法

用状态机代替简单的 if/else。

```javascript
// 简单粗暴的判断
function run() {
    if (!licensed) {
        showWatermark();
        return;
    }
    // 正常功能
}

// 状态机版本：让人找不到入口点
const STATES = {
    INIT: 0,
    CHECK: 1,
    DECIDE: 2,
    EXECUTE: 3,
    FALLBACK: 4
};

function stateMachine(state, data) {
    switch(state) {
        case STATES.INIT:
            return { next: STATES.CHECK, data: prepareData(data) };
        case STATES.CHECK:
            // 这里才真正做判断，但看起来像普通的状态转移
            const passed = verify(data);
            return { next: passed ? STATES.EXECUTE : STATES.FALLBACK };
        case STATES.EXECUTE:
            return { next: -1 };  // 正常流程
        case STATES.FALLBACK:
            return { next: -1 };  // 受限流程
    }
}
```

---

## 2. 利用编译器/构建工具特性

### 2.1 常量折叠

让关键判断在编译期就被算出结果。

```javascript
// 源代码
const SECRET = 0x5A;
const isValid = (input) => (input ^ SECRET) === 0x99;

// 编译后（如果走常量折叠）
// 变成了：input === 0xC3 时返回 true
// 分析工具可以直接算出逆运算
```

更好的方式：用运行时才有的值作为key。

```javascript
// 构建时替换的变量
const BUILD_KEY = "__BUILD_KEY__";  // 替换成具体的随机值

function check(key) {
    // 混淆后的逻辑看起来像随机运算
    return ((key * 2654435769) >>> 0) === BUILD_KEY;
}
```

### 2.2 代码加密/解密执行

核心逻辑加密，运行时解密。

```javascript
// 加密的函数体（实际使用时从服务器获取）
const encryptedLogic = "X7q9...二进制的密文";
const key = fetchKey();  // 动态获取key

// 解密并执行
const decrypted = decrypt(encryptedLogic, key);
const fn = new Function(decrypted);
fn();

// 注意：这种方式需要配合完整性校验，否则可以直接 Hook decrypt 函数 Dump 结果
```

### 2.3 WebAssembly / 字节码

把关键逻辑编译成 WASM，增加逆向难度。

```javascript
// 加载 WASM 模块
const wasmModule = WebAssembly.compile(wasmBinary);
const instance = new WebAssembly.Instance(wasmModule, {
    env: { /* 接口 */ }
});

// 调用在 WASM 里的判断函数
const result = instance.exports.checkLicense(key);
```

---

## 3. 行为检测而非特征检测

### 3.1 检测调试器

```javascript
// 检测调试器（Web端示例）
function detectDebugger() {
    // 1. 检测 devtools 是否打开
    const start = Date.now();
    debugger;  // 强制断点
    const delta = Date.now() - start;
    if (delta > 100) return true;  // 调试时会有明显延迟
    
    // 2. 检测 Chrome DevTools Protocol
    // 如果从 DevTools 打开页面，navigator.webdriver 会是 true
    if (navigator.webDriver) return true;
    
    // 3. 检测断点
    const originalConsole = console.log;
    console.log = function(...args) {
        // 被 Hook 了，说明在调试
        throw new Error("Console hooked!");
    };
}
```

### 3.2 检测 Hook 框架

```javascript
// 检测 Function.prototype 被修改
(function() {
    const original = Function.prototype.call;
    Function.prototype.call = function(...args) {
        // 被修改了，可能在调试
        return original.apply(this, args);
    };
    // 检测是否被修改
    if (Function.prototype.call.toString().indexOf("native code") === -1) {
        // 被 Hook 了
    }
})();

// 检测 setTimeout/setInterval 是否被修改
const originalSetTimeout = window.setTimeout;
window.setTimeout = function(fn, delay) {
    // 可能是调试工具在拦截
    return originalSetTimeout(fn, delay);
};
```

### 3.3 检测模拟器/虚拟机

```javascript
function detectVM() {
    // 1. 检测屏幕分辨率是否异常
    const screenProps = [screen.width, screen.height, screen.colorDepth];
    if (screenProps.some(p => p === 0 || p === undefined)) return true;
    
    // 2. 检测硬件信息
    const gl = document.createElement('canvas').getContext('webgl');
    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    if (debugInfo) {
        const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
        // VMware, VirtualBox, QEMU 等会有特征
        if (/VMware|VirtualBox|QEMU|llvmpipe/i.test(renderer)) return true;
    }
    
    // 3. 检测 CPU 核心数（很多浏览器沙箱会报告假值）
    const cores = navigator.hardwareConcurrency;
    if (cores < 2 || cores > 64) return true;
}
```

---

## 4. 服务端校验（最靠谱）

把判断逻辑放到服务器，客户端只负责展示。

```javascript
// 客户端：只发请求，不做判断
async function loadFeatures() {
    const token = getToken();
    const response = await fetch('/api/features', {
        headers: { 'Authorization': token }
    });
    const features = await response.json();
    
    // 服务器返回什么，客户端就展示什么
    applyFeatures(features);
}

// 服务器端：完整的校验逻辑
app.get('/api/features', async (req, res) => {
    const user = await verifyToken(req.headers.authorization);
    if (!user.license) {
        // 返回受限功能
        return res.json({ 
            pro: false, 
            maxProjects: 3,
            watermark: true 
        });
    }
    // 返回完整功能
    return res.json({ 
        pro: true, 
        maxProjects: -1,
        watermark: false 
    });
});
```

优势：
- 逻辑完全不可见
- 可以随时更新规则
- 可以做行为分析

---

## 5. 综合示例：多层防御

```javascript
class LicenseManager {
    constructor() {
        this.state = this.loadState();
    }
    
    // 第一层：静态检查（快速失败）
    quickCheck() {
        // 用分散的小判断组成
        const checks = [
            this.checkStorage(),
            this.checkTime(),
            this.checkDevice()
        ];
        // 全部通过才继续
        return checks.every(c => c);
    }
    
    // 第二层：运行时动态检查
    async verify() {
        // 发起服务器校验
        const result = await fetch('/api/verify', {
            body: JSON.stringify(this.collectFingerprint())
        }).then(r => r.json());
        
        this.state.verified = result.valid;
        return result.valid;
    }
    
    // 第三层：行为检测
    monitor() {
        // 后台持续检测异常行为
        setInterval(() => {
            if (this.detectDebug()) {
                this.state.compromised = true;
            }
        }, 5000);
    }
    
    // 核心功能：根据状态决定行为
    getFeatures() {
        // 不直接返回 boolean，而是返回具体的功能列表
        if (this.state.compromised) {
            return this.getLimitedFeatures();  // 静默降级
        }
        if (!this.state.verified) {
            return this.getTrialFeatures();
        }
        return this.getProFeatures();
    }
}
```

---

## 常见误区

| 误区 | 真相 |
|------|------|
| 混淆越复杂越安全 | 只是增加分析时间，无法阻止决心破解的人 |
| 加壳就能保护 | 壳本身也是被脱的对象 |
| 机器码/字节码安全 | 虚拟机保护才靠谱，但成本高 |
| 一次性判断就够 | 多层检查比单点判断更难全面绕过 |

---

## 总结

**没有绝对的保护，只有性价比的权衡。**

- 让破解成本 > 购买正版成本 = 成功
- 判断逻辑隐藏得越好，破解成本越高
- 行为检测比静态特征更难绕过
- 服务端校验是最终的避风港

真正的安全是**工程问题**，不是**技术问题**。

---

*本文仅代表个人观点，欢迎讨论交流*
