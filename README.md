# Shadowrocket 配置

基于 [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `lazy_group.conf`，增加长桥证券与富途证券独立分流。

## 导入

在 Shadowrocket 的「配置」页面点击右上角 `+`，粘贴：

```text
https://raw.githubusercontent.com/reallinzc/Shadowrocket/main/shadowrocket.conf
```

配置不会包含节点。请先在 Shadowrocket 中添加节点或订阅。

## 券商分流

- `长桥证券`：默认使用香港节点，也可切换新加坡节点、全局代理或直连。
- `富途证券`：默认使用香港节点，也可切换新加坡、美国节点、全局代理或直连。
- 两组规则位于通用国内外规则之前，可分别固定出口，避免被后续 `GEOIP,CN,DIRECT` 覆盖。

域名列表来自 GitHub 上维护的 [v2fly/domain-list-community/longbridge](https://github.com/v2fly/domain-list-community/blob/master/data/longbridge) 与 [v2fly/domain-list-community/futu](https://github.com/v2fly/domain-list-community/blob/master/data/futu)。GitHub Actions 每天北京时间 08:30 拉取上游、生成并校验配置。

## 文件

- `shadowrocket.conf`：可直接导入的完整配置。
- `rules/Longbridge.list`：长桥证券 Shadowrocket 规则集。
- `rules/Futu.list`：富途证券与 moomoo Shadowrocket 规则集。
- `scripts/build.py`：从上游生成发布文件。
- `scripts/validate.py`：检查配置结构、分流优先级及规则格式。

## 本地更新

```bash
python3 scripts/build.py
python3 scripts/validate.py
```

## 许可与来源

本仓库的衍生配置按 [CC BY-SA 4.0](LICENSE) 发布。第三方来源与许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
