# Web Service Template

## Getting started
### 配置
* update .env,参考.env copy

> **设计理念**
> * 首推MSE/Nacos，搭配云端组件，尤其面向复杂、项目体量较大、配置化运营
>   * 多基于BaseModel，采用默认参数，支持配置修改即可
> * 全部由.env托管维护，多级嵌套配置难维护，臃肿，可读性差
> * 倾向改参数，更新部署即可应用，免打包

### 启动/部署
### Local
``` shell
poetry install --no-root
uvicorn main:app
```
### Docker
根据最终架构策略调整`compose.yaml`
```shell
docker compose up -d
```


## Description
### 同步 or 异步？【仅个人观点】
> 异步【基于协程】
> * 优点
>    * 面向API,性能/速度相对会快一点
> * 缺点
>    * 第三方package[组件/库]异步支持程度堪忧，如celery,但整体前景较好

> 同步【基于多线程】
> * 优点
>    * 第三方package[组件/库]，基本无缝衔接
> * 缺点
>    * 遇到IO密集型，依赖更加优良的编程功底

## 版本迭代
没有最好的模版、只有更好的，或者自己用起来更顺手、项目契合度更高的
### 1.1.0
* 后续个人项目【Service】的模版方向
* 自研项目，配置更多以.env为主
    * 企业级可考虑.env结合MSE等云组件使用
* docker 配置以及相关组件的运用推荐融入到开发中
    * 类似K8s容器编排，偏运维方向，需要熟悉