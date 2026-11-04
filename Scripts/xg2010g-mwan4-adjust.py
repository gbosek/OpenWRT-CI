#!/usr/bin/env python3
from pathlib import Path

def replace(path, old, new):
    p = Path(path)
    text = p.read_text()
    if text.count(old) != 1:
        raise SystemExit(f'Unexpected source in {path}: {old!r}')
    p.write_text(text.replace(old, new, 1))

init = 'package/custom/mwan4/files/etc/init.d/mwan4'
replace(init, '[ -d "$MWAN4_STATUS_DIR" ]', 'procd_running mwan4 "${1:-*}"')
replace(init, 'reload_service() {\n\tstart\n}', 'reload_service() {\n\tservice_running || return 0\n\tstart\n}')
uc = 'package/custom/mwan4/files/lib/mwan4/mwan4.uc'
replace(uc, "return system('/etc/init.d/mwan4 start');", "return system('/etc/init.d/mwan4 enable && /etc/init.d/mwan4 start');")
replace(uc, "return system('/etc/init.d/mwan4 stop');", "return system('/etc/init.d/mwan4 disable && /etc/init.d/mwan4 stop');")
js = 'package/custom/luci-app-mwan4/htdocs/luci-static/resources/view/mwan4/network/overview.js'
p = Path(js)
s = p.read_text()
a = s.index('function saveApplyRestart() {')
b = s.index('\nfunction closeModal()', a)
s = s[:a] + '''function saveApplyRestart() {
	let wasRunning = false;
	return withBusy(byId('mwan4-app'), function() {
		return L.resolveDefault(callStatus(), {}).then(function(status) {
			wasRunning = !!((status.diagnostics || {}).service_running);
			return uci.save();
		}).then(function() { return uci.apply(10); })
		.then(function() { return hasOperatorAccess && wasRunning ? runMwan4([ 'restart' ]) : null; })
		.then(function() {
			ui.addNotification(null, E('p', [ wasRunning
				? _('MultiWAN 4 settings applied and service restarted.')
				: _('MultiWAN 4 settings applied. Service remains stopped.') ]), 'info');
		}).then(reloadOverview);
	});
}
''' + s[b:]
p.write_text(s)
po = Path('package/custom/luci-app-mwan4/po/zh_Hans/mwan4.po')
with po.open('a') as f:
    f.write('\nmsgid "MultiWAN 4 settings applied. Service remains stopped."\nmsgstr "MWAN4 设置已应用，服务保持停止。"\n')
