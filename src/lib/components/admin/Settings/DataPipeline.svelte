<script>
	import { getContext, onMount, onDestroy } from 'svelte';
	import { toast } from 'svelte-sonner';

	const i18n = getContext('i18n');

	// --- State ---
	let pipelineType = 'speech';
	let selectedTerms = [21];
	let shutdownRag = true;
	let exportExcel = false;
	let keepOlderData = true;
	let keepNewerData = true;
	let useGpu = false;

	let status = 'idle';
	let currentPipeline = null;
	let startedAt = null;
	let exitCode = null;
	let agentOnline = true;
	let triggering = false;

	let logLines = [];
	let logContainer;
	let autoScroll = true;
	let statusInterval = null;
	let sseActive = false;

	// --- Run History ---
	let historyTab = 'manifesto';
	let manifestoRuns = [];
	let speechRuns = [];
	let historyLoading = false;
	let expandedRunId = null;
	let runLogContent = '';
	let runLogLoading = false;
	let showHistory = true;

	const availableTerms = [17, 18, 19, 20, 21];

	// --- API Helpers ---
	const apiBase = '/api/v1/polapro';

	async function fetchStatus() {
		try {
			const resp = await fetch(`${apiBase}/pipeline/status`, {
				headers: { Authorization: `Bearer ${localStorage.token}` }
			});
			if (resp.ok) {
				agentOnline = true;
				const data = await resp.json();
				const prevStatus = status;
				status = data.status;
				currentPipeline = data.pipeline;
				startedAt = data.started_at;
				exitCode = data.exit_code;

				// If running and no SSE stream, connect
				if (status === 'running' && !sseActive) {
					connectLogStream(logLines.length);
				}

				// If status changed from running to completed/failed, refresh history
				if (prevStatus === 'running' && (status === 'completed' || status === 'failed')) {
					fetchRunHistory();
				}
			} else if (resp.status === 502 || resp.status === 503) {
				agentOnline = false;
			}
		} catch (e) {
			agentOnline = false;
			console.error('Failed to fetch pipeline status:', e);
		}
	}

	async function triggerPipeline() {
		if (selectedTerms.length === 0) {
			toast.error($i18n.t('Please select at least one electoral term.'));
			return;
		}

		triggering = true;

		try {
			const resp = await fetch(`${apiBase}/pipeline/trigger`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${localStorage.token}`
				},
				body: JSON.stringify({
					pipeline: pipelineType,
					shutdown_rag: shutdownRag,
					terms: selectedTerms,
					use_gpu: useGpu,
					export_excel: exportExcel,
					keep_older_data: keepOlderData,
					keep_newer_data: keepNewerData
				})
			});

			if (resp.ok) {
				const data = await resp.json();
				agentOnline = true;
				toast.success(
					$i18n.t('✅ Pipeline "{{pipeline}}" triggered successfully! PID: {{pid}}', {
						pipeline: data.pipeline || pipelineType,
						pid: data.pid || '?'
					})
				);
				status = 'running';
				currentPipeline = pipelineType;
				startedAt = new Date().toISOString();
				// Clear log buffer for the new run
				logLines = [];
				connectLogStream(0);
			} else if (resp.status === 409) {
				toast.error($i18n.t('A pipeline is already running. Please wait for it to finish.'));
			} else if (resp.status === 502 || resp.status === 503) {
				agentOnline = false;
				toast.error(
					$i18n.t(
						'Pipeline agent is not reachable (HTTP {{status}}). Check that pipeline-agent.service is running on the host.',
						{ status: resp.status }
					)
				);
			} else {
				const err = await resp.json().catch(() => ({ detail: 'Unknown error' }));
				toast.error(err.detail || 'Failed to trigger pipeline.');
			}
		} catch (e) {
			agentOnline = false;
			toast.error($i18n.t('Failed to connect to the pipeline agent.'));
			console.error('Trigger error:', e);
		} finally {
			triggering = false;
		}
	}

	async function cancelPipeline() {
		if (!confirm($i18n.t('Are you sure you want to cancel the running pipeline? The pipeline will perform a safety rollback.'))) {
			return;
		}
		try {
			const resp = await fetch(`${apiBase}/pipeline/cancel`, {
				method: 'POST',
				headers: { Authorization: `Bearer ${localStorage.token}` }
			});
			if (resp.ok) {
				toast.success($i18n.t('Cancel signal sent. The pipeline will shut down gracefully.'));
			} else {
				const err = await resp.json().catch(() => ({ detail: 'Unknown error' }));
				toast.error(err.detail || 'Failed to cancel pipeline.');
			}
		} catch (e) {
			toast.error($i18n.t('Failed to send cancel signal.'));
		}
	}

	function connectLogStream(fromLine) {
		if (sseActive) return;
		fetchSSE(fromLine);
	}

	async function fetchSSE(fromLine) {
		sseActive = true;
		try {
			const resp = await fetch(
				`${apiBase}/pipeline/logs/stream?from_line=${fromLine}`,
				{
					headers: { Authorization: `Bearer ${localStorage.token}` }
				}
			);

			if (!resp.ok) {
				console.error('SSE stream error:', resp.status);
				sseActive = false;
				return;
			}

			const reader = resp.body.getReader();
			const decoder = new TextDecoder();
			let buffer = '';

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				buffer += decoder.decode(value, { stream: true });
				const lines = buffer.split('\n');
				buffer = lines.pop() || '';

				for (const line of lines) {
					if (line.startsWith('data: ')) {
						try {
							const data = JSON.parse(line.slice(6));

							if (data.type === 'log') {
								logLines = [...logLines, data.content];
								if (autoScroll && logContainer) {
									requestAnimationFrame(() => {
										logContainer.scrollTop = logContainer.scrollHeight;
									});
								}
							} else if (data.type === 'complete') {
								exitCode = data.exit_code;
								status = data.exit_code === 0 ? 'completed' : 'failed';
								if (data.exit_code === 0) {
									toast.success($i18n.t('Pipeline completed successfully!'));
								} else {
									toast.error($i18n.t('Pipeline failed. Check the logs for details.'));
								}
								sseActive = false;
								fetchRunHistory();
								return;
							} else if (data.type === 'error') {
								logLines = [...logLines, `[ERROR] ${data.message}`];
							}
						} catch (parseErr) {
							// Skip malformed JSON
						}
					}
				}
			}
		} catch (e) {
			if (status === 'running') {
				console.warn('SSE stream disconnected, will retry on next status poll.', e);
			}
		} finally {
			sseActive = false;
		}
	}

	function toggleTerm(term) {
		if (selectedTerms.includes(term)) {
			selectedTerms = selectedTerms.filter((t) => t !== term);
		} else {
			selectedTerms = [...selectedTerms, term].sort();
		}
	}

	function handleLogScroll() {
		if (logContainer) {
			const { scrollTop, scrollHeight, clientHeight } = logContainer;
			autoScroll = scrollHeight - scrollTop - clientHeight < 50;
		}
	}

	function scrollToBottom() {
		autoScroll = true;
		if (logContainer) {
			logContainer.scrollTop = logContainer.scrollHeight;
		}
	}

	function copyLogs() {
		const text = logLines.join('\n');
		navigator.clipboard.writeText(text).then(
			() => toast.success($i18n.t('Logs copied to clipboard!')),
			() => toast.error($i18n.t('Failed to copy logs.'))
		);
	}

	function getElapsedTime(startIso) {
		if (!startIso) return '';
		const start = new Date(startIso);
		const now = new Date();
		const diff = Math.floor((now - start) / 1000);
		const h = Math.floor(diff / 3600);
		const m = Math.floor((diff % 3600) / 60);
		const s = diff % 60;
		if (h > 0) return `${h}h ${m}m ${s}s`;
		if (m > 0) return `${m}m ${s}s`;
		return `${s}s`;
	}

	function formatDuration(seconds) {
		if (seconds == null) return '—';
		const h = Math.floor(seconds / 3600);
		const m = Math.floor((seconds % 3600) / 60);
		const s = Math.round(seconds % 60);
		if (h > 0) return `${h}h ${m}m ${s}s`;
		if (m > 0) return `${m}m ${s}s`;
		return `${s}s`;
	}

	function formatDate(iso) {
		if (!iso) return '—';
		return new Date(iso).toLocaleString('de-DE', {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		});
	}

	let elapsedDisplay = '';
	let elapsedInterval;

	$: if (status === 'running' && startedAt) {
		clearInterval(elapsedInterval);
		elapsedInterval = setInterval(() => {
			elapsedDisplay = getElapsedTime(startedAt);
		}, 1000);
	} else {
		clearInterval(elapsedInterval);
		elapsedDisplay = '';
	}

	// --- Run History ---
	async function fetchRunHistory() {
		historyLoading = true;
		try {
			const [mResp, sResp] = await Promise.all([
				fetch(`${apiBase}/pipeline/runs/manifesto`, {
					headers: { Authorization: `Bearer ${localStorage.token}` }
				}),
				fetch(`${apiBase}/pipeline/runs/speech`, {
					headers: { Authorization: `Bearer ${localStorage.token}` }
				})
			]);
			if (mResp.ok) {
				const mData = await mResp.json();
				manifestoRuns = (mData.runs || []).sort((a, b) => b.run_id - a.run_id);
			}
			if (sResp.ok) {
				const sData = await sResp.json();
				speechRuns = (sData.runs || []).sort((a, b) => b.run_id - a.run_id);
			}
		} catch (e) {
			console.error('Failed to fetch run history:', e);
		} finally {
			historyLoading = false;
		}
	}

	async function viewRunLog(pipelineType, runId) {
		if (expandedRunId === `${pipelineType}-${runId}`) {
			expandedRunId = null;
			runLogContent = '';
			return;
		}
		expandedRunId = `${pipelineType}-${runId}`;
		runLogLoading = true;
		runLogContent = '';
		try {
			const resp = await fetch(`${apiBase}/pipeline/runs/${pipelineType}/${runId}/log`, {
				headers: { Authorization: `Bearer ${localStorage.token}` }
			});
			if (resp.ok) {
				const data = await resp.json();
				runLogContent = data.content || 'No content.';
			} else if (resp.status === 404) {
				runLogContent = '⚠️ Log file not found. It may have been archived or deleted.';
			} else {
				runLogContent = `Error loading log: HTTP ${resp.status}`;
			}
		} catch (e) {
			runLogContent = `Error loading log: ${e.message}`;
		} finally {
			runLogLoading = false;
		}
	}

	function copyRunLog() {
		navigator.clipboard.writeText(runLogContent).then(
			() => toast.success($i18n.t('Log copied to clipboard!')),
			() => toast.error($i18n.t('Failed to copy log.'))
		);
	}

	onMount(() => {
		fetchStatus();
		fetchRunHistory();
		statusInterval = setInterval(fetchStatus, 10000);

		setTimeout(async () => {
			if (!agentOnline) {
				toast.warning(
					$i18n.t('Pipeline agent is not reachable. Pipelines cannot be triggered until the agent is online.')
				);
			}
		}, 2000);
	});

	onDestroy(() => {
		if (statusInterval) clearInterval(statusInterval);
		if (elapsedInterval) clearInterval(elapsedInterval);
	});
</script>

<!-- {$i18n.t('Data Pipeline')} -->

<div class="flex flex-col gap-4">
	<!-- Agent connectivity warning -->
	{#if !agentOnline}
		<div
			class="flex items-center gap-2 px-4 py-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 text-sm"
		>
			<span class="text-lg">⚠️</span>
			<div>
				<strong>{$i18n.t('Pipeline Agent Offline')}</strong>
				<span class="ml-1 text-amber-600 dark:text-amber-400">
					{$i18n.t('The host agent (pipeline-agent.service) is not reachable. Run: sudo systemctl status pipeline-agent.service')}
				</span>
			</div>
		</div>
	{/if}

	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h2 class="text-lg font-semibold dark:text-gray-100">
				{$i18n.t('Data Pipeline')}
			</h2>
			<p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
				{$i18n.t('Manage speech and manifesto data generation pipelines.')}
			</p>
		</div>

		<!-- Status Badge -->
		<div class="flex items-center gap-2">
			{#if status === 'running'}
				<span
					class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
				>
					<span class="relative flex h-2 w-2">
						<span
							class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"
						></span>
						<span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
					</span>
					{$i18n.t('Running')}
					{#if currentPipeline}({currentPipeline}){/if}
					{#if elapsedDisplay}
						<span class="text-blue-600 dark:text-blue-400">— {elapsedDisplay}</span>
					{/if}
				</span>
			{:else if status === 'completed'}
				<span
					class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300"
				>
					<span class="h-2 w-2 rounded-full bg-green-500"></span>
					{$i18n.t('Completed')}
				</span>
			{:else if status === 'failed'}
				<span
					class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300"
				>
					<span class="h-2 w-2 rounded-full bg-red-500"></span>
					{$i18n.t('Failed')}
				</span>
			{:else}
				<span
					class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
				>
					<span class="h-2 w-2 rounded-full bg-gray-400"></span>
					{$i18n.t('Idle')}
				</span>
			{/if}
		</div>
	</div>

	<hr class="dark:border-gray-800" />

	<!-- Configuration Section -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
		<!-- Left Column: Pipeline Selection -->
		<div class="flex flex-col gap-4">
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					{$i18n.t('Select Pipeline')}
				</label>
				<div class="flex gap-3">
					<button
						class="flex-1 px-4 py-2.5 rounded-lg border text-sm font-medium transition-all {pipelineType ===
						'speech'
							? 'border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-600 ring-1 ring-blue-500/20'
							: 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600'}"
						on:click={() => (pipelineType = 'speech')}
						disabled={status === 'running'}
					>
						🏛️ {$i18n.t('Speech')}
					</button>
					<button
						class="flex-1 px-4 py-2.5 rounded-lg border text-sm font-medium transition-all {pipelineType ===
						'manifesto'
							? 'border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-600 ring-1 ring-blue-500/20'
							: 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600'}"
						on:click={() => (pipelineType = 'manifesto')}
						disabled={status === 'running'}
					>
						📜 {$i18n.t('Manifesto')}
					</button>
				</div>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					{$i18n.t('Electoral Terms')}
				</label>
				<div class="flex flex-wrap gap-2">
					{#each availableTerms as term}
						<button
							class="px-3 py-1.5 rounded-lg border text-sm font-medium transition-all {selectedTerms.includes(
								term
							)
								? 'border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-600'
								: 'border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600'}"
							on:click={() => toggleTerm(term)}
							disabled={status === 'running'}
						>
							{term}. WP
						</button>
					{/each}
				</div>
			</div>
		</div>

		<!-- Right Column: Options -->
		<div class="flex flex-col gap-3">
			<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
				{$i18n.t('Options')}
			</label>

			<!-- Toggle: Shutdown RAG -->
			<label class="flex items-center justify-between cursor-pointer group">
				<div>
					<span class="text-sm text-gray-700 dark:text-gray-300"
						>{$i18n.t('Shutdown RAG during update')}</span
					>
					<p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
						{$i18n.t('Stops the RAG service and shows a maintenance banner.')}
					</p>
				</div>
				<input
					type="checkbox"
					bind:checked={shutdownRag}
					disabled={status === 'running'}
					class="sr-only peer"
				/>
				<div
					class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-500"
				></div>
			</label>

			<!-- Toggle: Export Excel -->
			<label class="flex items-center justify-between cursor-pointer group">
				<span class="text-sm text-gray-700 dark:text-gray-300">{$i18n.t('Export to Excel')}</span>
				<input type="checkbox" bind:checked={exportExcel} disabled={status === 'running'} class="sr-only peer" />
				<div class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-500"></div>
			</label>

			<!-- Toggle: Keep Older Data -->
			<label class="flex items-center justify-between cursor-pointer group">
				<span class="text-sm text-gray-700 dark:text-gray-300">{$i18n.t('Keep older data')}</span>
				<input type="checkbox" bind:checked={keepOlderData} disabled={status === 'running'} class="sr-only peer" />
				<div class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-500"></div>
			</label>

			<!-- Toggle: Keep Newer Data -->
			<label class="flex items-center justify-between cursor-pointer group">
				<span class="text-sm text-gray-700 dark:text-gray-300">{$i18n.t('Keep newer data')}</span>
				<input type="checkbox" bind:checked={keepNewerData} disabled={status === 'running'} class="sr-only peer" />
				<div class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-500"></div>
			</label>

			<!-- Toggle: Use GPU -->
			<label class="flex items-center justify-between cursor-pointer group">
				<span class="text-sm text-gray-700 dark:text-gray-300">{$i18n.t('Use local GPU')}</span>
				<input type="checkbox" bind:checked={useGpu} disabled={status === 'running'} class="sr-only peer" />
				<div class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-500"></div>
			</label>
		</div>
	</div>

	<hr class="dark:border-gray-800" />

	<!-- Action Buttons -->
	<div class="flex items-center gap-3">
		<button
			class="px-5 py-2.5 rounded-lg text-sm font-medium transition-all
				{status === 'running' || selectedTerms.length === 0 || triggering || !agentOnline
				? 'bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-gray-800 dark:text-gray-600'
				: 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 shadow-sm hover:shadow'}"
			on:click={triggerPipeline}
			disabled={status === 'running' || selectedTerms.length === 0 || triggering || !agentOnline}
		>
			{#if triggering}
				{$i18n.t('Triggering...')}
			{:else if status === 'running'}
				{$i18n.t('Pipeline Running...')}
			{:else}
				▶ {$i18n.t('Run Pipeline')}
			{/if}
		</button>

		{#if status === 'running'}
			<button
				class="px-5 py-2.5 rounded-lg text-sm font-medium bg-red-50 text-red-600 hover:bg-red-100 active:bg-red-200 dark:bg-red-900/20 dark:text-red-400 dark:hover:bg-red-900/30 transition-all border border-red-200 dark:border-red-800"
				on:click={cancelPipeline}
			>
				⏹ {$i18n.t('Cancel Pipeline')}
			</button>
		{/if}

		{#if selectedTerms.length === 0}
			<span class="text-xs text-amber-500 dark:text-amber-400">
				{$i18n.t('Select at least one electoral term to enable the run button.')}
			</span>
		{/if}
	</div>

	<!-- Log Console -->
	<div class="flex flex-col gap-2">
		<div class="flex items-center justify-between">
			<label class="text-sm font-medium text-gray-700 dark:text-gray-300">
				{$i18n.t('Pipeline Logs')}
				{#if logLines.length > 0}
					<span class="text-xs text-gray-400 ml-1">({logLines.length} lines)</span>
				{/if}
			</label>

			<div class="flex items-center gap-2">
				{#if logLines.length > 0}
					<button
						class="text-xs px-2 py-1 rounded bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 transition-colors"
						on:click={copyLogs}
						title={$i18n.t('Copy all logs')}
					>
						📋 {$i18n.t('Copy')}
					</button>
				{/if}

				{#if logLines.length > 0 && !autoScroll}
					<button
						class="text-xs text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 transition-colors"
						on:click={scrollToBottom}
					>
						↓ {$i18n.t('Scroll to bottom')}
					</button>
				{/if}
			</div>
		</div>

		<div
			bind:this={logContainer}
			on:scroll={handleLogScroll}
			class="bg-gray-950 rounded-lg p-4 h-[700px] overflow-y-auto font-mono text-xs text-gray-300 leading-relaxed border border-gray-800"
		>
			{#if logLines.length === 0}
				<div class="flex items-center justify-center h-full text-gray-600">
					{#if status === 'running'}
						<span class="animate-pulse">{$i18n.t('Waiting for log output...')}</span>
					{:else}
						{$i18n.t('No logs available. Trigger a pipeline to see output here.')}
					{/if}
				</div>
			{:else}
				{#each logLines as line, idx}
					<div
						class="py-0.5 {line.includes('ERROR') || line.includes('CRITICAL')
							? 'text-red-400'
							: line.includes('WARNING')
								? 'text-amber-400'
								: line.includes('Successfully') || line.includes('completed successfully') || line.includes('PASSED')
									? 'text-green-400'
									: line.includes('SIGTERM')
										? 'text-orange-400'
										: ''}"
					>
						<span class="text-gray-600 select-none mr-2">{String(idx + 1).padStart(4, ' ')}</span
						>{line}
					</div>
				{/each}
			{/if}
		</div>
	</div>

	<hr class="dark:border-gray-800" />

	<!-- Run History Section -->
	<div class="flex flex-col gap-3">
		<button
			class="flex items-center justify-between w-full text-left"
			on:click={() => (showHistory = !showHistory)}
		>
			<h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300">
				📊 {$i18n.t('Run History')}
				<span class="text-xs font-normal text-gray-400 ml-1">
					({manifestoRuns.length + speechRuns.length} runs)
				</span>
			</h3>
			<span class="text-gray-400 text-xs">{showHistory ? '▼' : '▶'}</span>
		</button>

		{#if showHistory}
			<!-- History Tabs -->
			<div class="flex gap-2 border-b border-gray-200 dark:border-gray-700">
				<button
					class="px-3 py-1.5 text-sm font-medium border-b-2 transition-colors {historyTab === 'manifesto'
						? 'border-blue-500 text-blue-600 dark:text-blue-400'
						: 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}"
					on:click={() => (historyTab = 'manifesto')}
				>
					📜 Manifesto ({manifestoRuns.length})
				</button>
				<button
					class="px-3 py-1.5 text-sm font-medium border-b-2 transition-colors {historyTab === 'speech'
						? 'border-blue-500 text-blue-600 dark:text-blue-400'
						: 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}"
					on:click={() => (historyTab = 'speech')}
				>
					🏛️ Speech ({speechRuns.length})
				</button>
			</div>

			{#if historyLoading}
				<div class="flex items-center justify-center py-8 text-gray-500">
					<span class="animate-pulse">{$i18n.t('Loading run history...')}</span>
				</div>
			{:else}
				{@const runs = historyTab === 'manifesto' ? manifestoRuns : speechRuns}
				{#if runs.length === 0}
					<div class="text-center py-6 text-gray-500 dark:text-gray-400 text-sm">
						{$i18n.t('No runs recorded yet for this pipeline.')}
					</div>
				{:else}
					<div class="flex flex-col gap-3">
						{#each runs as run (run.run_id)}
							{@const isExpanded = expandedRunId === `${historyTab}-${run.run_id}`}
							<div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
								<!-- Run Card Header -->
								<div class="p-3 bg-gray-50 dark:bg-gray-850">
									<div class="flex items-center justify-between">
										<div class="flex items-center gap-2">
											<span class="text-sm font-mono font-semibold text-gray-700 dark:text-gray-300">
												#{run.run_id}
											</span>
											{#if run.success}
												<span class="px-2 py-0.5 rounded text-[10px] font-medium bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
													✓ Success
												</span>
											{:else}
												<span class="px-2 py-0.5 rounded text-[10px] font-medium bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400">
													✗ Failed
												</span>
											{/if}
											<span class="text-xs text-gray-500 dark:text-gray-400">
												{formatDate(run.start_time)}
											</span>
										</div>
										<div class="flex items-center gap-2">
											<span class="text-xs text-gray-500 dark:text-gray-400">
												⏱ {formatDuration(run.duration_seconds)}
											</span>
											{#if run.log_available}
												<button
													class="text-xs px-2 py-1 rounded bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300 transition-colors"
													on:click={() => viewRunLog(historyTab, run.run_id)}
												>
													{isExpanded ? '▼ Hide Log' : '📄 View Log'}
												</button>
											{:else}
												<span class="text-xs text-gray-400 italic">No log</span>
											{/if}
										</div>
									</div>

									<!-- Parameters & Stats -->
									<div class="mt-2 grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
										{#if run.parameters}
											<div class="bg-white dark:bg-gray-800 rounded px-2 py-1">
												<span class="text-gray-400">Terms:</span>
												<span class="text-gray-700 dark:text-gray-300 ml-1">
													{(run.parameters.terms || []).map((t) => `${t}. WP`).join(', ') || '—'}
												</span>
											</div>
											{#if run.parameters.export_excel !== undefined}
												<div class="bg-white dark:bg-gray-800 rounded px-2 py-1">
													<span class="text-gray-400">Excel:</span>
													<span class="text-gray-700 dark:text-gray-300 ml-1">{run.parameters.export_excel ? 'Yes' : 'No'}</span>
												</div>
											{/if}
											{#if run.parameters.use_gpu !== undefined}
												<div class="bg-white dark:bg-gray-800 rounded px-2 py-1">
													<span class="text-gray-400">GPU:</span>
													<span class="text-gray-700 dark:text-gray-300 ml-1">{run.parameters.use_gpu ? 'Yes' : 'No'}</span>
												</div>
											{/if}
										{/if}
										{#if run.stats}
											{#if run.stats.manifestos_processed != null}
												<div class="bg-white dark:bg-gray-800 rounded px-2 py-1">
													<span class="text-gray-400">Manifestos:</span>
													<span class="text-gray-700 dark:text-gray-300 ml-1">{run.stats.manifestos_processed}</span>
												</div>
											{/if}
											{#if run.stats.chunks_generated != null}
												<div class="bg-white dark:bg-gray-800 rounded px-2 py-1">
													<span class="text-gray-400">Chunks:</span>
													<span class="text-gray-700 dark:text-gray-300 ml-1">{run.stats.chunks_generated}</span>
												</div>
											{/if}
											{#if run.stats.chunks_ingested_count != null}
												<div class="bg-white dark:bg-gray-800 rounded px-2 py-1">
													<span class="text-gray-400">Ingested:</span>
													<span class="text-gray-700 dark:text-gray-300 ml-1">{run.stats.chunks_ingested_count}</span>
												</div>
											{/if}
											{#if run.stats.sentences_processed != null}
												<div class="bg-white dark:bg-gray-800 rounded px-2 py-1">
													<span class="text-gray-400">Sentences:</span>
													<span class="text-gray-700 dark:text-gray-300 ml-1">{run.stats.sentences_processed?.toLocaleString()}</span>
												</div>
											{/if}
											{#if run.stats.speeches_processed != null}
												<div class="bg-white dark:bg-gray-800 rounded px-2 py-1">
													<span class="text-gray-400">Speeches:</span>
													<span class="text-gray-700 dark:text-gray-300 ml-1">{run.stats.speeches_processed?.toLocaleString()}</span>
												</div>
											{/if}
											{#if run.stats.weaviate_integrity_check}
												<div class="bg-white dark:bg-gray-800 rounded px-2 py-1">
													<span class="text-gray-400">DB Check:</span>
													<span class="ml-1 {run.stats.weaviate_integrity_check.status === 'PASS' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}">
														{run.stats.weaviate_integrity_check.status}
													</span>
													{#if run.stats.weaviate_integrity_check.document_count}
														<span class="text-gray-400 ml-1">({run.stats.weaviate_integrity_check.document_count} docs)</span>
													{/if}
												</div>
											{/if}
										{/if}
									</div>

									<!-- Step Durations -->
									{#if run.step_durations && Object.keys(run.step_durations).length > 0}
										<div class="mt-2 flex flex-wrap gap-1.5">
											{#each Object.entries(run.step_durations) as [step, duration]}
												<span class="px-2 py-0.5 rounded-full text-[10px] bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300 border border-blue-100 dark:border-blue-800">
													{step}: {formatDuration(duration)}
												</span>
											{/each}
										</div>
									{/if}
								</div>

								<!-- Expanded Log Viewer -->
								{#if isExpanded}
									<div class="border-t border-gray-200 dark:border-gray-700">
										{#if runLogLoading}
											<div class="flex items-center justify-center py-8 text-gray-500">
												<span class="animate-pulse">{$i18n.t('Loading log...')}</span>
											</div>
										{:else}
											<div class="flex items-center justify-end px-3 py-1 bg-gray-100 dark:bg-gray-800">
												<button
													class="text-xs px-2 py-1 rounded bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300 transition-colors"
													on:click={copyRunLog}
												>
													📋 {$i18n.t('Copy Log')}
												</button>
											</div>
											<div class="bg-gray-950 p-3 max-h-[1000px] overflow-y-auto font-mono text-xs text-gray-300 leading-relaxed whitespace-pre-wrap">
												{#if runLogContent.startsWith('⚠️')}
													<div class="text-amber-400 py-4 text-center">{runLogContent}</div>
												{:else}
													{runLogContent}
												{/if}
											</div>
										{/if}
									</div>
								{/if}
							</div>
						{/each}
					</div>
				{/if}
			{/if}
		{/if}
	</div>
</div>
