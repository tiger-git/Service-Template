# Web Service Template

## Getting started
### 配置
* update config/config.yaml

> **设计理念**
> * 深度尽可能不要超过3
> * 多基于Item，采用默认参数，支持配置修改即可
> * 配置参数越少越好，除环境相关参数，尽可能用常量/Item方案代替或优化

### 启动/部署

* `poetry install --no-root`
    * 根据需要移除package jinjia2 [or templates],或其他无用package
* `uvicorn main:app`

## Description
### 同步 or 异步？【仅个人观点】
> 异步【基于协程】
> * 优点
>    * 面向API,性能/速度相对会快一点
> * 缺点
>    * 第三方package[组件/库]异步支持程度堪忧，如celery

> 同步【基于多线程】
> * 优点
>    * 第三方package[组件/库]，基本无缝衔接
> * 缺点
>    * 遇到IO密集型，依赖更加优良的编程功底

## 版本迭代
没有最好的模版、只有更好的，或者自己用起来更顺手、项目契合度更高的
### 1.0.0
* 初版
* 后续个人项目的模版方向