<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import type { Writable } from 'svelte/store';
	import Modal from '../common/Modal.svelte';
	import { WEBUI_API_BASE_URL } from '$lib/constants';
	import Spinner from '../common/Spinner.svelte';

	const i18n: Writable<any> = getContext('i18n');

	export let show = false;

	let loading = false;

	// Survey form state
	let satisfaction = '';
	let accuracy = '';
	let usability = '';
	let missingFeatures = '';
	let additionalComments = '';

	const satisfactionOptions = [
		{ value: 'sehr_zufrieden', label: 'Sehr zufrieden' },
		{ value: 'zufrieden', label: 'Zufrieden' },
		{ value: 'neutral', label: 'Neutral' },
		{ value: 'unzufrieden', label: 'Unzufrieden' },
		{ value: 'sehr_unzufrieden', label: 'Sehr unzufrieden' }
	];

	const accuracyOptions = [
		{ value: 'sehr_genau', label: 'Sehr genau' },
		{ value: 'meistens_genau', label: 'Meistens genau' },
		{ value: 'manchmal_genau', label: 'Manchmal genau' },
		{ value: 'selten_genau', label: 'Selten genau' },
		{ value: 'nie_genau', label: 'Nie genau' }
	];

	const usabilityOptions = [
		{ value: 'sehr_einfach', label: 'Sehr einfach' },
		{ value: 'einfach', label: 'Einfach' },
		{ value: 'mittel', label: 'Mittel' },
		{ value: 'schwierig', label: 'Schwierig' },
		{ value: 'sehr_schwierig', label: 'Sehr schwierig' }
	];

	const resetForm = () => {
		satisfaction = '';
		accuracy = '';
		usability = '';
		missingFeatures = '';
		additionalComments = '';
	};

	const submitSurvey = async () => {
		if (!satisfaction && !accuracy && !usability && !missingFeatures && !additionalComments) {
			toast.error('Bitte beantworten Sie mindestens eine Frage.');
			return;
		}

		loading = true;

		try {
			const res = await fetch(`${WEBUI_API_BASE_URL}/evaluations/questionnaire`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${localStorage.token}`
				},
				body: JSON.stringify({
					responses: {
						satisfaction,
						accuracy,
						usability,
						missing_features: missingFeatures,
						additional_comments: additionalComments
					},
					user_agent: navigator.userAgent
				})
			});

			if (res.ok) {
				toast.success('Vielen Dank für Ihr Feedback!');
				resetForm();
				show = false;
			} else {
				const data = await res.json().catch(() => ({}));
				toast.error(data?.detail || 'Fehler beim Absenden des Fragebogens.');
			}
		} catch (e) {
			toast.error('Fehler beim Absenden des Fragebogens.');
			console.error('Survey submit error:', e);
		} finally {
			loading = false;
		}
	};
</script>

<Modal bind:show size="sm">
	<div class="px-6 py-5">
		<!-- Header -->
		<div class="flex items-center justify-between mb-5">
			<div class="flex items-center gap-2.5">
				<div class="flex items-center justify-center size-9 rounded-xl bg-blue-500/10 dark:bg-blue-400/10">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke-width="1.5"
						stroke="currentColor"
						class="size-5 text-blue-600 dark:text-blue-400"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15a2.25 2.25 0 0 1 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z"
						/>
					</svg>
				</div>
				<div>
					<h3 class="text-lg font-semibold text-gray-900 dark:text-white">Feedback-Fragebogen</h3>
					<p class="text-xs text-gray-500 dark:text-gray-400">Helfen Sie uns, PoLaPro zu verbessern</p>
				</div>
			</div>

			<button
				class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition"
				on:click={() => (show = false)}
			>
				<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4.5 text-gray-400">
					<path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
				</svg>
			</button>
		</div>

		<!-- Form -->
		<div class="space-y-5">
			<!-- Q1: Satisfaction -->
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					Wie zufrieden sind Sie insgesamt mit PoLaPro?
				</label>
				<div class="flex flex-wrap gap-2">
					{#each satisfactionOptions as option}
						<button
							class="px-3 py-1.5 text-sm rounded-xl border transition
								{satisfaction === option.value
									? 'bg-blue-500 text-white border-blue-500 dark:bg-blue-600 dark:border-blue-600'
									: 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'}"
							on:click={() => (satisfaction = satisfaction === option.value ? '' : option.value)}
						>
							{option.label}
						</button>
					{/each}
				</div>
			</div>

			<!-- Q2: Accuracy -->
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					Wie bewerten Sie die Genauigkeit der Antworten?
				</label>
				<div class="flex flex-wrap gap-2">
					{#each accuracyOptions as option}
						<button
							class="px-3 py-1.5 text-sm rounded-xl border transition
								{accuracy === option.value
									? 'bg-blue-500 text-white border-blue-500 dark:bg-blue-600 dark:border-blue-600'
									: 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'}"
							on:click={() => (accuracy = accuracy === option.value ? '' : option.value)}
						>
							{option.label}
						</button>
					{/each}
				</div>
			</div>

			<!-- Q3: Usability -->
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					Wie einfach ist die Bedienung?
				</label>
				<div class="flex flex-wrap gap-2">
					{#each usabilityOptions as option}
						<button
							class="px-3 py-1.5 text-sm rounded-xl border transition
								{usability === option.value
									? 'bg-blue-500 text-white border-blue-500 dark:bg-blue-600 dark:border-blue-600'
									: 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'}"
							on:click={() => (usability = usability === option.value ? '' : option.value)}
						>
							{option.label}
						</button>
					{/each}
				</div>
			</div>

			<!-- Q4: Missing Features -->
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					Welche Funktionen vermissen Sie?
				</label>
				<textarea
					bind:value={missingFeatures}
					rows="2"
					class="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 dark:border-gray-700 bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40 resize-none"
					placeholder="z.B. bessere Filteroptionen, Export-Funktion, ..."
				></textarea>
			</div>

			<!-- Q5: Additional Comments -->
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					Sonstige Anmerkungen
				</label>
				<textarea
					bind:value={additionalComments}
					rows="2"
					class="w-full px-3 py-2 text-sm rounded-xl border border-gray-200 dark:border-gray-700 bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40 resize-none"
					placeholder="Ihre Anregungen und Kommentare ..."
				></textarea>
			</div>
		</div>

		<!-- Footer Buttons -->
		<div class="flex justify-end gap-2 mt-6">
			<button
				class="px-4 py-2 text-sm font-medium rounded-xl border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 transition"
				on:click={() => {
					resetForm();
					show = false;
				}}
			>
				Abbrechen
			</button>
			<button
				class="px-4 py-2 text-sm font-medium rounded-xl bg-blue-500 hover:bg-blue-600 text-white transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
				disabled={loading}
				on:click={submitSurvey}
			>
				{#if loading}
					<Spinner className="size-4" />
				{/if}
				Absenden
			</button>
		</div>
	</div>
</Modal>
