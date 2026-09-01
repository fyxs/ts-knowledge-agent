import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function App() {
  return <main className="shell"><header><span className="eyebrow">TS KNOWLEDGE AGENT</span><h1>团队知识处理工作台</h1><p>本地扫描 · 转换 · 沉淀 · 搜索</p></header><section className="cards"><article><b>本地知识源</b><span>等待配置</span></article><article><b>处理状态</b><span>骨架阶段</span></article><article><b>AG-UI</b><span>SSE 默认</span></article></section><section className="panel"><h2>搜索共享知识</h2><p>搜索服务和 AG-UI 对话界面将在后续垂直切片中接入。</p><div className="search"><input placeholder="输入关键词或问题" disabled /><button disabled>搜索</button></div></section></main>
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
