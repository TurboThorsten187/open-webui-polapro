<script lang="ts">
	import { getContext } from 'svelte';
	import Dropdown from '$lib/components/common/Dropdown.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import { polaproConfig } from '$lib/polapro_config';

	const i18n = getContext('i18n');

	export let show = false;
	export let metadata = {
		speakers: [] as string[],
		parties: [] as string[],
		roles: [] as string[],
		electoralTerms: [] as string[],
		dateFrom: '',
		dateTo: '',
		manifestoParties: [] as string[],
		manifestoYearFrom: '',
		manifestoYearTo: '',
		manifestoThemes: [] as string[]
	};

	let newSpeaker = '';
	let themeSearchQuery = '';

	const speechParties = [
		'CDU/CSU',
		'SPD',
		'Bündnis 90/Die Grünen',
		'DIE LINKE.',
		'AfD',
		'FDP',
		'BSW',
		'Fraktionslos'
	];

	const manifestoPartiesList = [
		'CDU/CSU',
		'SPD',
		'Bündnis 90/Die Grünen',
		'DIE LINKE.',
		'AfD',
		'FDP',
		'BSW'
	];

	const roleLabels = [
		{ value: 'Member of Parliament', label: 'Abgeordnete/r (MdB)' },
		{ value: 'Minister', label: 'Bundesminister/in' },
		{ value: 'Secretary of State', label: 'Staatssekretär/in' },
		{ value: 'Chancellor', label: 'Bundeskanzler/in' },
		{ value: 'Presidium of Parliament', label: 'Bundestagspräsidium' },
		{ value: 'Guest', label: 'Gastredner/in' },
		{ value: 'Not found', label: 'Keine Rolle/Sonstige' }
	];

	const CMP_MAP: Record<string, string> = {
		'101': 'Auslandsbeziehungen: Positiv',
		'102': 'Auslandsbeziehungen: Negativ',
		'103': 'Antimilitarismus',
		'104': 'Militär: Positiv',
		'105': 'Militär: Negativ',
		'106': 'Frieden',
		'107': 'Internationale Kooperation',
		'108': 'Europäische Integration: Positiv',
		'109': 'Europäische Integration: Negativ',
		'110': 'Internationale Sicherheit',
		'201': 'Freiheit und Menschenrechte',
		'202': 'Demokratie',
		'203': 'Verfassungsstaat/Rechtsstaat',
		'204': 'Verfassungsreform',
		'301': 'Dezentralisierung',
		'302': 'Zentralisierung',
		'303': 'Effizienz der Verwaltung',
		'304': 'Korruptionsbekämpfung',
		'305': 'Politisches System: Positiv',
		'401': 'Freie Marktwirtschaft',
		'402': 'Marktregulierung',
		'403': 'Wirtschaftliche Entwicklung',
		'404': 'Infrastruktur/Technologie',
		'405': 'Korporatismus/Sozialpartnerschaft',
		'406': 'Protektionismus: Positiv',
		'407': 'Protektionismus: Negativ',
		'408': 'Wirtschaftliche Ziele',
		'409': 'Verstaatlichung',
		'410': 'Wirtschaftliche Planung',
		'411': 'Technologie und Wissenschaft',
		'412': 'Arbeitnehmerrechte: Positiv',
		'413': 'Arbeitnehmerrechte: Negativ',
		'414': 'Wirtschaftswachstum',
		'415': 'Agrarpolitik',
		'416': 'Verbraucherschutz',
		'501': 'Umweltschutz',
		'502': 'Kultur/Wissenschaft: Positiv',
		'503': 'Gleichheit/Gerechtigkeit',
		'504': 'Sozialstaat: Ausbau',
		'505': 'Sozialstaat: Einschränkung',
		'506': 'Bildungsausbau',
		'507': 'Bildungseinschränkung',
		'601': 'Nationale Lebensweise: Positiv',
		'602': 'Nationale Lebensweise: Negativ',
		'603': 'Traditionelle Moral: Positiv',
		'604': 'Traditionelle Moral: Negativ',
		'605': 'Recht und Ordnung',
		'606': 'Nationaler Zusammenhalt',
		'607': 'Multikulturalismus: Positiv',
		'608': 'Multikulturalismus: Negativ',
		'701': 'Arbeiterschaft: Positiv',
		'702': 'Arbeiterschaft: Negativ',
		'703': 'Landwirte: Positiv',
		'704': 'Mittelstand/Unternehmer: Positiv',
		'705': 'Minderheiten: Positiv',
		'706': 'Ältere Menschen: Positiv'
	};

	$: filteredThemes = Object.entries(CMP_MAP).filter(([code, name]) => {
		return name.toLowerCase().includes(themeSearchQuery.toLowerCase()) || code.includes(themeSearchQuery);
	});

	function addSpeaker() {
		const name = newSpeaker.trim();
		if (name && !metadata.speakers.includes(name)) {
			metadata.speakers = [...metadata.speakers, name];
			newSpeaker = '';
		}
	}

	function removeSpeaker(index: number) {
		metadata.speakers = metadata.speakers.filter((_, i) => i !== index);
	}

	function resetFilters() {
		metadata = {
			speakers: [],
			parties: [],
			roles: [],
			electoralTerms: [],
			dateFrom: '',
			dateTo: '',
			manifestoParties: [],
			manifestoYearFrom: '',
			manifestoYearTo: '',
			manifestoThemes: []
		};
		newSpeaker = '';
		themeSearchQuery = '';
	}
</script>

<Dropdown bind:show side="top">
	<Tooltip content={$i18n.t('Filter')} placement="top">
		<slot />
	</Tooltip>
	<div slot="content">
		<div class="px-5 py-4 min-w-[42rem] max-w-[48rem] rounded-2xl border border-gray-100 dark:border-gray-800 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-lg flex flex-col overflow-hidden" style="max-height: inherit;">
			<!-- Header -->
			<div class="font-semibold text-lg border-b pb-2 border-gray-100 dark:border-gray-800 text-gray-900 dark:text-white flex-shrink-0">
				{$i18n.t('Filter')}
			</div>

			<!-- Scrollable middle content -->
			<div class="grid grid-cols-2 gap-8 divide-x divide-gray-100 dark:divide-gray-800 overflow-y-auto py-2 my-1 flex-1 min-h-0 scrollbar-hidden">
				<!-- Left Column: Bundestagsreden -->
				<div class="flex flex-col gap-4 pr-4">
					<div class="font-semibold text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b pb-1.5 border-gray-100 dark:border-gray-800">
						{$i18n.t('Bundestagsreden')}
					</div>

					<!-- Speakers (Namen) -->
					{#if polaproConfig.metadataFields.speakers}
						<div class="flex flex-col gap-1.5">
							<label class="text-xs font-semibold text-gray-500 dark:text-gray-400">{$i18n.t('Redner (Namen)')}</label>
							<div class="flex flex-wrap gap-1.5 mb-1">
								{#each metadata.speakers as speaker, i}
									<span class="inline-flex items-center gap-1 bg-gray-50 dark:bg-gray-800/60 text-gray-700 dark:text-gray-300 text-xs px-2.5 py-1 rounded-lg font-medium border border-gray-100 dark:border-gray-800">
										{speaker}
										<button type="button" class="hover:text-gray-900 dark:hover:text-white text-gray-400 font-bold" on:click={() => removeSpeaker(i)}>&times;</button>
									</span>
								{/each}
							</div>
							<div class="flex gap-1.5">
								<input
									type="text"
									bind:value={newSpeaker}
									on:keydown={(e) => {
										if (e.key === 'Enter') {
											e.preventDefault();
											addSpeaker();
										}
									}}
									class="flex-1 bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-sky-500 text-sm py-1.5 px-3"
									placeholder={$i18n.t('Name hinzufügen...')}
								/>
								<button type="button" class="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-800 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-200 rounded-lg text-sm font-medium transition-colors" on:click={addSpeaker}>
									+
								</button>
							</div>
						</div>
					{/if}

					<!-- Parties (Fraktionen) -->
					{#if polaproConfig.metadataFields.parties}
						<div class="flex flex-col gap-1.5">
							<label class="text-xs font-semibold text-gray-500 dark:text-gray-400">{$i18n.t('Fraktionen')}</label>
							<div class="grid grid-cols-2 gap-2 mt-1">
								{#each speechParties as party}
									<label class="flex items-center gap-2 cursor-pointer text-xs text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100">
										<input
											type="checkbox"
											value={party}
											bind:group={metadata.parties}
											class="rounded border-gray-300 dark:border-gray-700 dark:bg-gray-800 text-sky-600 focus:ring-sky-500"
										/>
										<span>{party}</span>
									</label>
								{/each}
							</div>
						</div>
					{/if}

					<!-- Roles (Rollen) -->
					{#if polaproConfig.metadataFields.roles}
						<div class="flex flex-col gap-1.5">
							<label class="text-xs font-semibold text-gray-500 dark:text-gray-400">{$i18n.t('Rollen')}</label>
							<div class="grid grid-cols-2 gap-2 mt-1">
								{#each roleLabels as role}
									<label class="flex items-center gap-2 cursor-pointer text-xs text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100">
										<input
											type="checkbox"
											value={role.value}
											bind:group={metadata.roles}
											class="rounded border-gray-300 dark:border-gray-700 dark:bg-gray-800 text-sky-600 focus:ring-sky-500"
										/>
										<span>{role.label}</span>
									</label>
								{/each}
							</div>
						</div>
					{/if}

					<!-- Electoral Terms (Wahlperioden) -->
					{#if polaproConfig.metadataFields.electoralTerms}
						<div class="flex flex-col gap-1.5">
							<label class="text-xs font-semibold text-gray-500 dark:text-gray-400">{$i18n.t('Wahlperioden')}</label>
							<div class="flex gap-4 mt-1">
								<label class="flex items-center gap-2 cursor-pointer text-xs text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100">
									<input
										type="checkbox"
										value="19"
										bind:group={metadata.electoralTerms}
										class="rounded border-gray-300 dark:border-gray-700 dark:bg-gray-800 text-sky-600 focus:ring-sky-500"
									/>
									<span>19. Wahlperiode</span>
								</label>
								<label class="flex items-center gap-2 cursor-pointer text-xs text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100">
									<input
										type="checkbox"
										value="20"
										bind:group={metadata.electoralTerms}
										class="rounded border-gray-300 dark:border-gray-700 dark:bg-gray-800 text-sky-600 focus:ring-sky-500"
									/>
									<span>20. Wahlperiode</span>
								</label>
							</div>
						</div>
					{/if}

					<!-- Date Range (Zeitraum) -->
					{#if polaproConfig.metadataFields.dateRange}
						<div class="flex flex-col gap-1.5">
							<label class="text-xs font-semibold text-gray-500 dark:text-gray-400">{$i18n.t('Zeitraum (Datum von - bis)')}</label>
							<div class="flex gap-2 items-center mt-1">
								<input
									type="date"
									bind:value={metadata.dateFrom}
									class="flex-1 bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-sky-500 text-sm py-1.5 px-3 text-gray-700 dark:text-gray-200 cursor-pointer"
									on:click={(e) => {
										try {
											e.currentTarget.showPicker();
										} catch (err) {}
									}}
								/>
								<span class="text-xs text-gray-500">{$i18n.t('bis')}</span>
								<input
									type="date"
									bind:value={metadata.dateTo}
									class="flex-1 bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-sky-500 text-sm py-1.5 px-3 text-gray-700 dark:text-gray-200 cursor-pointer"
									on:click={(e) => {
										try {
											e.currentTarget.showPicker();
										} catch (err) {}
									}}
								/>
							</div>
						</div>
					{/if}
				</div>

				<!-- Right Column: Wahlprogramme -->
				<div class="flex flex-col gap-4 pl-8">
					<div class="font-semibold text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b pb-1.5 border-gray-100 dark:border-gray-800">
						{$i18n.t('Wahlprogramme')}
					</div>

					<!-- Manifesto Parties -->
					{#if polaproConfig.metadataFields.manifestoParties}
						<div class="flex flex-col gap-1.5">
							<label class="text-xs font-semibold text-gray-500 dark:text-gray-400">{$i18n.t('Parteien')}</label>
							<div class="grid grid-cols-2 gap-2 mt-1">
								{#each manifestoPartiesList as party}
									<label class="flex items-center gap-2 cursor-pointer text-xs text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100">
										<input
											type="checkbox"
											value={party}
											bind:group={metadata.manifestoParties}
											class="rounded border-gray-300 dark:border-gray-700 dark:bg-gray-800 text-sky-600 focus:ring-sky-500"
										/>
										<span>{party}</span>
									</label>
								{/each}
							</div>
						</div>
					{/if}

					<!-- Manifesto Years Range -->
					{#if polaproConfig.metadataFields.manifestoYearRange}
						<div class="flex flex-col gap-1.5">
							<label class="text-xs font-semibold text-gray-500 dark:text-gray-400">{$i18n.t('Zeitraum (Jahr von - bis)')}</label>
							<div class="flex gap-2 items-center mt-1">
								<input
									type="number"
									min="1949"
									max="2100"
									placeholder="z.B. 2017"
									bind:value={metadata.manifestoYearFrom}
									class="flex-1 bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-sky-500 text-sm py-1.5 px-3 text-gray-700 dark:text-gray-200"
								/>
								<span class="text-xs text-gray-500">{$i18n.t('bis')}</span>
								<input
									type="number"
									min="1949"
									max="2100"
									placeholder="z.B. 2021"
									bind:value={metadata.manifestoYearTo}
									class="flex-1 bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-sky-500 text-sm py-1.5 px-3 text-gray-700 dark:text-gray-200"
								/>
							</div>
						</div>
					{/if}

					<!-- Manifesto Themes (CMP Codes) -->
					{#if polaproConfig.metadataFields.manifestoThemes}
						<div class="flex flex-col gap-1.5">
							<label class="text-xs font-semibold text-gray-500 dark:text-gray-400">{$i18n.t('Themen (CMP)')}</label>
							<div class="flex flex-col gap-1.5 mt-1">
								<input
									type="text"
									bind:value={themeSearchQuery}
									placeholder={$i18n.t('Themen durchsuchen...')}
									class="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-sky-500 text-xs py-1.5 px-2.5"
								/>
								<div class="max-h-[14rem] overflow-y-auto border border-gray-150 dark:border-gray-800 rounded-lg p-2.5 flex flex-col gap-2 bg-gray-50/50 dark:bg-gray-800/20">
									{#each filteredThemes as [code, label]}
										<label class="flex items-start gap-2 cursor-pointer text-xs text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100">
											<input
												type="checkbox"
												value={code}
												bind:group={metadata.manifestoThemes}
												class="rounded border-gray-300 dark:border-gray-700 dark:bg-gray-800 text-sky-600 focus:ring-sky-500 mt-0.5"
											/>
											<span><span class="font-semibold text-gray-400 dark:text-gray-500 mr-1">{code}</span>{label}</span>
										</label>
									{/each}
								</div>
							</div>
						</div>
					{/if}
				</div>
			</div>

			<!-- Footer -->
			<div class="mt-4 flex justify-between items-center gap-2 border-t pt-3 border-gray-100 dark:border-gray-800 flex-shrink-0">
				<button
					type="button"
					class="bg-gray-100 hover:bg-gray-200 text-gray-800 dark:text-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 rounded-lg px-4 py-2 text-sm font-medium transition-colors"
					on:click={resetFilters}
				>
					{$i18n.t('Zurücksetzen')}
				</button>

				<button
					type="button"
					class="bg-gray-900 hover:bg-gray-850 text-white dark:bg-gray-100 dark:hover:bg-white dark:text-gray-900 rounded-lg px-4 py-2 text-sm font-medium transition-colors"
					on:click={() => (show = false)}
				>
					{$i18n.t('Speichern')}
				</button>
			</div>
		</div>
	</div>
</Dropdown>