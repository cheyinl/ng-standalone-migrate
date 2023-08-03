#!/usr/bin/env python3

from typing import Any, Dict, Tuple, Iterable, Optional

from collections import namedtuple
import sys
import logging
import os
import re

_log = logging.getLogger(__name__)

ImportDefSetting = namedtuple('ImportDefSetting', ('cluster_index', 'import_stmts'))

IMPORT_DEFS = {
		'common':
				ImportDefSetting(0, (r"import { CommonModule } from '@angular/common';", )),
		'form':
				ImportDefSetting(0, (r"import { FormsModule } from '@angular/forms';", )),
		'reactiveform':
				ImportDefSetting(0, (r"import { ReactiveFormsModule } from '@angular/forms';", )),
		'cdkclipboard':
				ImportDefSetting(1, (r"import { ClipboardModule } from '@angular/cdk/clipboard';", )),
		'cdktextfield':
				ImportDefSetting(1, (r"import { TextFieldModule } from '@angular/cdk/text-field';", )),
		'autocomplete':
				ImportDefSetting(2, (r"import { MatAutocompleteModule } from '@angular/material/autocomplete';", )),
		'badge':
				ImportDefSetting(2, (r"import { MatBadgeModule } from '@angular/material/badge';", )),
		'button':
				ImportDefSetting(2, (r"import { MatButtonModule } from '@angular/material/button';", )),
		'button-toggle':
				ImportDefSetting(2, (r"import { MatButtonToggleModule } from '@angular/material/button-toggle';", )),
		'card':
				ImportDefSetting(2, (r"import { MatCardModule } from '@angular/material/card';", )),
		'checkbox':
				ImportDefSetting(2, (r"import { MatCheckboxModule } from '@angular/material/checkbox';", )),
		'chips':
				ImportDefSetting(2, (r"import { MatChipsModule } from '@angular/material/chips';", )),
		'datepicker':
				ImportDefSetting(2, (r"import { MatDatepickerModule } from '@angular/material/datepicker';", )),
		'dialog':
				ImportDefSetting(2, (r"import { MatDialogModule, MatDialog } from '@angular/material/dialog';", )),
		'divider':
				ImportDefSetting(2, (r"import { MatDividerModule } from '@angular/material/divider';", )),
		'expansion-panel':
				ImportDefSetting(2, (r"import { MatExpansionModule } from '@angular/material/expansion';", )),
		'form-field':
				ImportDefSetting(2, (r"import { MatFormFieldModule } from '@angular/material/form-field';", )),
		'grid-list':
				ImportDefSetting(2, (r"import { MatGridListModule } from '@angular/material/grid-list';", )),
		'icon':
				ImportDefSetting(2, (r"import { MatIconModule } from '@angular/material/icon';", )),
		'input':
				ImportDefSetting(2, (r"import { MatInputModule } from '@angular/material/input';", )),
		'list':
				ImportDefSetting(2, (r"import { MatListModule } from '@angular/material/list';", )),
		'menu':
				ImportDefSetting(2, (r"import { MatMenuModule } from '@angular/material/menu';", )),
		'paginator':
				ImportDefSetting(2, (r"import { MatPaginatorModule } from '@angular/material/paginator';", )),
		'progressbar':
				ImportDefSetting(2, (r"import { MatProgressBarModule } from '@angular/material/progress-bar';", )),
		'spinner':
				ImportDefSetting(2, (r"import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';", )),
		'radiogroup':
				ImportDefSetting(2, (r"import { MatRadioModule } from '@angular/material/radio';", )),
		'select':
				ImportDefSetting(2, (r"import { MatSelectModule } from '@angular/material/select';", )),
		'slidetoggle':
				ImportDefSetting(2, (r"import { MatSlideToggleModule } from '@angular/material/slide-toggle';", )),
		'slider':
				ImportDefSetting(2, (r"import { MatSliderModule } from '@angular/material/slider';", )),
		'snackbar':
				ImportDefSetting(2, (r"import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';", )),
		'sort-header':
				ImportDefSetting(2, (r"import { MatSortModule } from '@angular/material/sort';", )),
		'stepper':
				ImportDefSetting(2, (r"import { MatStepperModule } from '@angular/material/stepper';", )),
		'table':
				ImportDefSetting(2, (r"import { MatTableModule } from '@angular/material/table';", )),
		'tab':
				ImportDefSetting(2, (r"import { MatTabsModule } from '@angular/material/tabs';", )),
		'toolbar':
				ImportDefSetting(2, (r"import { MatToolbarModule } from '@angular/material/toolbar';", )),
		'tooltip':
				ImportDefSetting(2, (r"import { MatTooltipModule } from '@angular/material/tooltip';", )),
		'tree':
				ImportDefSetting(2, (r"import { MatTreeModule } from '@angular/material/tree';", )),
		'enablement-state-picker':
				ImportDefSetting(3, (r"import { EnablementState } from '../midev-components/enablement-state';", )),
		'ident-token-code':
				ImportDefSetting(3, (r"import { IdentTokenCodeComponent } from '../midev-components/ident-token-code/ident-token-code.component';", )),
		'json-input-t1':
				ImportDefSetting(3, (r"import { JSONInputT1Component } from '../midev-components/json-input-t1/json-input-t1.component';", )),
		'operation-result-e1':
				ImportDefSetting(3, (r"import { OperationResultNoticeE1Module, OperationResultNoticeE1 } from '../midev-components/operation-result-e1';", )),
		'pipe-unix-timestamp':
				ImportDefSetting(3, (r"import { UnixTimestampPipe } from '../midev-components/unix-timestamp.pipe';", )),
}

DEF_CLUSTER_INDEX_BOUND = 0


def _update_def_cluster_index_bound() -> int:
	global DEF_CLUSTER_INDEX_BOUND
	DEF_CLUSTER_INDEX_BOUND = max(map(lambda x: x.cluster_index, IMPORT_DEFS.values())) + 1
	return DEF_CLUSTER_INDEX_BOUND


MODULE_TRAPS_HTML = {
		'ngIf': 'common',
		'ngFor': 'common',
		'ngSwitch': 'common',
		'ngModel': 'form',
		'formGroup': 'reactiveform',
		'mat-autocomplete': 'autocomplete',
		'matBadge': 'badge',
		'button': 'button',
		'matButton': 'button',
		'mat-button-toggle': 'button-toggle',
		'mat-card': 'card',
		'mat-checkbox': 'checkbox',
		'mat-basic-chip': 'chips',
		'mat-chip': 'chips',
		'matDatepicker': 'datepicker',
		'mat-date-range-picker': 'datepicker',
		'matStartDate': 'datepicker',
		'matEndDate': 'datepicker',
		'mat-calendar': 'datepicker',
		'mat-datepicker': 'datepicker',
		'matDatepickerToggleIcon': 'datepicker',
		'mat-datepicker-toggle': 'datepicker',
		'mat-divider': 'divider',
		'mat-expansion-panel': 'expansion-panel',
		'mat-form-field': 'form-field',
		'mat-label': 'form-field',
		'mat-error': 'form-field',
		'matError': 'form-field',
		'mat-grid-list': 'grid-list',
		'mat-icon': 'icon',
		'input': 'input',
		'textarea': 'input',
		'select': 'input',
		'matInput': 'input',
		'mat-list': 'list',
		'mat-menu': 'menu',
		'matMenu': 'menu',
		'matMenuTrigger': 'menu',
		'mat-menu-trigger-for': 'menu',
		'matMenuTriggerFor': 'menu',
		'mat-menu-item': 'menu',
		'mat-paginator': 'paginator',
		'matPaginator': 'paginator',
		'mat-progress-bar': 'progressbar',
		'mat-progress-spinner': 'spinner',
		'mat-spinner': 'spinner',
		'mat-radio-group': 'radiogroup',
		'mat-select': 'select',
		'mat-slide-toggle': 'slidetoggle',
		'mat-slider': 'slider',
		'mat-sort-header': 'sort-header',
		'mat-step': 'stepper',
		'mat-table': 'table',
		'matTabContent': 'tab',
		'mat-toolbar': 'toolbar',
		'matTooltip': 'tooltip',
		'mat-tree': 'tree',
		'cdkCopyToClipboard': 'cdkclipboard',
		'cdkAutofill': 'cdktextfield',
		'cdkTextareaAutosize': 'cdktextfield',
		'midev-enablement-state-picker': 'enablement-state-picker',
		'midev-ident-token-code': 'ident-token-code',
		'midev-json-input-t1': 'json-input-t1',
		'unixTimestamp': 'pipe-unix-timestamp',
}

MODULE_TRAPS_CODE = {
		r'(private|protected|public)\s+[a-zA-Z0-9_]+:\s+MatDialog': 'dialog',
		r'(private|protected|public)\s+[a-zA-Z0-9_]+:\s+MatSnackBar': 'snackbar',
		r'(private|protected|public)\s+[a-zA-Z0-9_]+:\s+OperationResultNoticeE1': 'operation-result-e1',
}

IMPORT_MODULE_EXTRACT_REGEX = re.compile(r"import\s*{\s*([A-Za-z0-9]+)(\s*(,\s+[A-Za-z0-9]+)+)?\s*}\s*")

STOP_FOLDERS = (
		'.angular',
		'.git',
		'.hg',
		'.vscode',
		'node_modules',
		'e2e',
		'dist',
		'assets',
		'midev-components',
)


class DefElement:
	def __init__(self, def_key: str, import_def_setting: ImportDefSetting) -> None:
		self.def_key = def_key
		self.cluster_index = import_def_setting.cluster_index
		self.import_defs = import_def_setting.import_stmts
		self.import_mods = []
		for line in import_def_setting.import_stmts:
			m = IMPORT_MODULE_EXTRACT_REGEX.match(line)
			if not m:
				continue
			self.import_mods.append(m.group(1))


class HTMLTrap:
	def __init__(self, trap_tag: str, import_def: DefElement) -> None:
		self.trap_regex = re.compile(r'(<|\s+|\(|\[|\|\s*|\*)' + trap_tag + r'(>|\s+|\)|\]|=|/|\s*}})')
		self.import_def = import_def


class CodeTrap:
	def __init__(self, trap_code: str, import_def: DefElement) -> None:
		self.trap_regex = re.compile(trap_code)
		self.import_def = import_def


class TrapWork:
	def __init__(self, traps_html: Iterable[HTMLTrap], traps_code: Iterable[CodeTrap]) -> None:
		self.traps_html = traps_html
		self.traps_code = traps_code
		self.def_elems: Dict[str, DefElement] = {}

	def feed_html_line(self, line: str) -> None:
		line = line + ' '
		for t in self.traps_html:
			m = t.trap_regex.search(line)
			if not m:
				continue
			self.def_elems[t.import_def.def_key] = t.import_def
			_log.debug('have element: %s: %r', t.import_def.def_key, line)

	def feed_code_line(self, line: str) -> None:
		for t in self.traps_code:
			m = t.trap_regex.search(line)
			if not m:
				continue
			self.def_elems[t.import_def.def_key] = t.import_def

	def export_import_code(self) -> Tuple[Iterable[str], Iterable[str]]:
		hdr_imports = []
		ann_imports = []
		for cluster_index in range(DEF_CLUSTER_INDEX_BOUND):
			hdr_imps = set()
			ann_imps = set()
			for idef in self.def_elems.values():
				if idef.cluster_index != cluster_index:
					continue
				if idef.import_defs:
					hdr_imps.update(idef.import_defs)
				if idef.import_mods:
					ann_imps.update(idef.import_mods)
			if hdr_imps:
				hdr_c = list(hdr_imps)
				hdr_c.sort()
				if hdr_imports:
					hdr_imports.append('')
				hdr_imports.extend(hdr_c)
			if ann_imps:
				ann_c = list(ann_imps)
				ann_c.sort()
				if ann_imports:
					ann_imports.append('')
				ann_imports.extend(ann_c)
		return (hdr_imports, ann_imports)


class TrapWorkFactory:
	def __init__(self, traps_html: Iterable[HTMLTrap], traps_code: Iterable[CodeTrap]) -> None:
		self.traps_html = traps_html
		self.traps_code = traps_code

	def __call__(self) -> TrapWork:
		return TrapWork(self.traps_html, self.traps_code)


def prepare_traps() -> TrapWorkFactory:
	def_elems = {}
	for def_key, import_defs in IMPORT_DEFS.items():
		def_elems[def_key] = DefElement(def_key, import_defs)
	traps_html = []
	for trap_tag, def_key in MODULE_TRAPS_HTML.items():
		imp_def = def_elems.get(def_key)
		if not imp_def:
			_log.warning('import definition key for html:[%s] not found: [%s]', trap_tag, def_key)
			continue
		traps_html.append(HTMLTrap(trap_tag, imp_def))
	traps_code = []
	for trap_code, def_key in MODULE_TRAPS_CODE.items():
		imp_def = def_elems.get(def_key)
		if not imp_def:
			_log.warning('import definition key for code:[%s] not found: [%s]', trap_code, def_key)
			continue
		traps_code.append(CodeTrap(trap_code, imp_def))
	return TrapWorkFactory(traps_html, traps_code)


def extract_module_requirement(trap_work_factory: TrapWorkFactory, path_html: str, path_ts: str) -> Tuple[Iterable[str], Iterable[str]]:
	trap_work = trap_work_factory()
	with open(path_html, 'r', encoding='utf-8') as fp:
		for line in fp:
			trap_work.feed_html_line(line)
	with open(path_ts, 'r', encoding='utf-8') as fp:
		for line in fp:
			trap_work.feed_code_line(line)
	return trap_work.export_import_code()


def walk_folder(trap_work_factory: TrapWorkFactory, target_folder: str) -> None:
	for dirpath, dirnames, filenames in os.walk(target_folder):
		filenames.sort()
		for fname in filenames:
			f_n, f_ext = os.path.splitext(fname)
			if f_ext != '.html':
				continue
			tsname = f_n + '.ts'
			if tsname not in filenames:
				_log.info('cannot reach .ts counter part: [%s/%s]', dirpath, fname)
				continue
			path_html = os.path.join(dirpath, fname)
			path_ts = os.path.join(dirpath, tsname)
			hdr_imports, ann_imports = extract_module_requirement(trap_work_factory, path_html, path_ts)
			_log.info('* process [%s]', path_html)
			if hdr_imports:
				_log.info("imports: ---\n%s\n---", "\n".join(hdr_imports))
			else:
				_log.info('imports: =empty=')
			if ann_imports:
				_log.info("annotation-imports: ---\n%s\n---", "\n".join(ann_imports))
			else:
				_log.info('annotation-imports: =empty=')
		for dname in STOP_FOLDERS:
			if dname in dirnames:
				dirnames.remove(dname)
		dirnames.sort()


COMPONENT_DEF_TRAP0 = re.compile(r'@Component\(')
COMPONENT_DEF_TRAP1 = re.compile(r"""\s*selector:\s*('|")([a-zA-Z0-9-_]+)('|")""")
COMPONENT_DEF_TRAP2 = re.compile(r'\s*export\s+class\s+([a-zA-Z0-9_]+)')


def scan_component_definition(path_ts: str, cluster_index: int) -> Tuple[Optional[str], ImportDefSetting]:
	selectorText = None
	componentClassName = None
	with open(path_ts, 'r', encoding='utf-8') as fp:
		state = 0
		for line in fp:
			if state == 0:
				m = COMPONENT_DEF_TRAP0.match(line)
				if m:
					state = 1
			elif state == 1:
				m = COMPONENT_DEF_TRAP1.match(line)
				if m:
					state = 2
					selectorText = m.group(2)
			elif state == 2:
				m = COMPONENT_DEF_TRAP2.match(line)
				if m:
					state = 3
					componentClassName = m.group(1)
					break
	if (not selectorText) or (not componentClassName):
		return (None, None)
	path_0, c_filename = os.path.split(path_ts)
	c_path = os.path.basename(path_0)
	c_modulename = c_filename[:-3]
	return (
			selectorText,
			ImportDefSetting(cluster_index, (f"import {{ {componentClassName} }} from '../{c_path}/{c_modulename}';", )),
	)


def scan_folder_n_expand_traps(target_folder: str) -> None:
	cluster_index = DEF_CLUSTER_INDEX_BOUND
	modified_traps = False
	for dirpath, dirnames, filenames in os.walk(target_folder):
		filenames.sort()
		for fname in filenames:
			if not fname.endswith('component.ts'):
				continue
			path_ts = os.path.join(dirpath, fname)
			_log.info('* scan for component [%s]', path_ts)
			app_selector, app_import_def_setting = scan_component_definition(path_ts, cluster_index)
			if not app_selector:
				continue
			_log.info("found component: %r", app_selector)
			def_key = "x-app-" + app_selector
			if def_key in IMPORT_DEFS:
				_log.warning("existed definition key in IMPORT_DEFS: %r (not adding found component)", def_key)
				continue
			if app_selector in MODULE_TRAPS_HTML:
				_log.warning("existed selector in MODULE_TRAPS_HTML: %r (not adding found component)", app_selector)
				continue
			IMPORT_DEFS[def_key] = app_import_def_setting
			MODULE_TRAPS_HTML[app_selector] = def_key
			modified_traps = True
		for dname in STOP_FOLDERS:
			if dname in dirnames:
				dirnames.remove(dname)
		dirnames.sort()
	if modified_traps:
		_update_def_cluster_index_bound()
	_log.info("*** -- scan_folder_n_expand_traps completed: modified_traps=%r", modified_traps)


_HELP_TEXT = """
Argument: [Options] [FOLDER_PATH]...

Options:
	--scan-component
		Enable component definition scan.
	-v
		Set logging level to DEBUG for more verbose logs.
	--help | -h
		Show this message.

""".replace("\t", "    ")


def parse_param() -> Tuple[Any, bool, Iterable[str]]:
	log_level = logging.INFO
	scan_component = False
	target_folders = []
	for arg in sys.argv[1:]:
		if arg == '--scan-component':
			scan_component = True
		elif arg == '-v':
			log_level = logging.DEBUG
		elif arg in ('--help', '-h'):
			print(_HELP_TEXT)
			raise SystemExit(1)
		else:
			arg = os.path.abspath(arg)
			target_folders.append(arg)
	return (
			log_level,
			scan_component,
			target_folders,
	)


def main():
	if len(sys.argv) < 2:
		print(_HELP_TEXT)
		raise SystemExit(1)
	log_level, scan_component, target_folders = parse_param()
	logging.basicConfig(level=log_level, stream=sys.stderr)
	_update_def_cluster_index_bound()
	if scan_component:
		for target_path in target_folders:
			scan_folder_n_expand_traps(target_path)
	_log.debug('DEF_CLUSTER_INDEX_BOUND = %d', DEF_CLUSTER_INDEX_BOUND)
	trap_work_factory = prepare_traps()
	for target_path in target_folders:
		walk_folder(trap_work_factory, target_path)


if __name__ == '__main__':
	main()
