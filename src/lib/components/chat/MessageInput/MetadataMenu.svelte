<script lang="ts">
	import { getContext } from 'svelte';
	import Dropdown from '$lib/components/common/Dropdown.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import { polaproConfig } from '$lib/polapro_config';

	const i18n = getContext('i18n');

	export let show = false;
	export let metadata = {
		firstName: '',
		lastName: '',
		party: '',
		role: '',
		electoralTerm: '',
		dateFrom: '',
		dateTo: '',
		speechId: ''
	};
</script>

<Dropdown bind:show>
	<Tooltip content={$i18n.t('Metadaten')} placement="top">
		<slot />
	</Tooltip>
	<div slot="content">
		<div class="px-4 py-3 min-w-[20rem] max-w-[24rem] rounded-2xl border border-gray-100 dark:border-gray-800 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-lg flex flex-col gap-3 max-h-96 overflow-y-auto">
			<div class="font-medium text-lg mb-1">{$i18n.t('Metadaten')}</div>

			{#if polaproConfig.metadataFields.firstName}
				<div class="flex flex-col gap-1">
					<label class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Vorname')}</label>
					<input type="text" bind:value={metadata.firstName} class="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-blue-500 text-sm py-1.5 px-3" placeholder={$i18n.t('Vorname')} />
				</div>
			{/if}

			{#if polaproConfig.metadataFields.lastName}
				<div class="flex flex-col gap-1">
					<label class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Nachname')}</label>
					<input type="text" bind:value={metadata.lastName} class="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-blue-500 text-sm py-1.5 px-3" placeholder={$i18n.t('Nachname')} />
				</div>
			{/if}

			{#if polaproConfig.metadataFields.party}
				<div class="flex flex-col gap-1">
					<label class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Fraktion/Partei')}</label>
					<select bind:value={metadata.party} class="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-blue-500 text-sm py-1.5 px-3">
						<option value="">{$i18n.t('Auswählen...')}</option>
						<option value="CDU/CSU">CDU/CSU</option>
						<option value="SPD">SPD</option>
						<option value="Die Grünen">Die Grünen</option>
						<option value="Die Linke">Die Linke</option>
						<option value="AfD">AfD</option>
						<option value="FDP">FDP</option>
					</select>
				</div>
			{/if}

			{#if polaproConfig.metadataFields.role}
				<div class="flex flex-col gap-1">
					<label class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Position/Rolle')}</label>
					<input type="text" bind:value={metadata.role} class="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-blue-500 text-sm py-1.5 px-3" placeholder={$i18n.t('Position/Rolle')} />
				</div>
			{/if}

			{#if polaproConfig.metadataFields.electoralTerm}
				<div class="flex flex-col gap-1">
					<label class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Wahlperiode')}</label>
					<select bind:value={metadata.electoralTerm} class="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-blue-500 text-sm py-1.5 px-3">
						<option value="">{$i18n.t('Auswählen...')}</option>
						<option value="19.">19.</option>
						<option value="20.">20.</option>
					</select>
				</div>
			{/if}

			{#if polaproConfig.metadataFields.dateRange}
				<div class="flex flex-col gap-1">
					<label class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Datum (von - bis)')}</label>
					<div class="flex gap-2 w-full">
						<input type="date" bind:value={metadata.dateFrom} class="w-1/2 bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-blue-500 text-sm py-1.5 px-3" />
						<span class="self-center text-gray-500">-</span>
						<input type="date" bind:value={metadata.dateTo} class="w-1/2 bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-blue-500 text-sm py-1.5 px-3" />
					</div>
				</div>
			{/if}

			{#if polaproConfig.metadataFields.speechId}
				<div class="flex flex-col gap-1">
					<label class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Rede-ID')}</label>
					<input type="text" bind:value={metadata.speechId} class="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-blue-500 text-sm py-1.5 px-3" placeholder={$i18n.t('Rede-ID')} />
				</div>
			{/if}
            
            <div class="mt-2 flex justify-between items-center gap-2">
                <button type="button" class="bg-gray-100 hover:bg-gray-200 text-gray-800 dark:text-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors" on:click={() => {
                    metadata = {
                        firstName: '',
                        lastName: '',
                        party: '',
                        role: '',
                        electoralTerm: '',
                        dateFrom: '',
                        dateTo: '',
                        speechId: ''
                    };
                }}>
                    {$i18n.t('Zurücksetzen')}
                </button>

                <button type="button" class="bg-white hover:bg-gray-50 text-gray-900 border border-gray-200 dark:border-gray-700 dark:bg-gray-100 dark:hover:bg-white dark:text-gray-900 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors" on:click={() => show = false}>
                    {$i18n.t('Speichern')}
                </button>
            </div>
		</div>
	</div>
</Dropdown>