<script lang="ts">
	import { LinkPreview } from 'bits-ui';
	import { decodeString } from '$lib/utils';
	import Source from './Source.svelte';
	import type { PolaProCitation } from '$lib/utils/citation-utils';
	import { activeCitation } from '$lib/stores';

	export let id;
	export let token;
	export let sourceIds = [];
	export let polaproCitations: PolaProCitation[] = [];
	export let onClick: Function = () => {};

	let openPreview = false;

	// Resolve citation data for this token
	$: citationId = token?.ids?.[0] ?? null;
	$: citation = citationId
		? (polaproCitations ?? []).find((c) => c.id === citationId)
		: null;
	$: hasPolaProData = citation !== null && citation !== undefined;

	function showCitation() {
		if (citation) {
			activeCitation.set(citation);
		}
	}

	// --- Fallback helpers (unchanged from original) ---
	function getDomain(url: string): string {
		const domain = url.replace('http://', '').replace('https://', '').split(/[/?#]/)[0];
		if (domain.startsWith('www.')) {
			return domain.slice(4);
		}
		return domain;
	}

	function formattedTitle(title: string): string {
		if (title.startsWith('http')) {
			return getDomain(title);
		}
		return title;
	}

	const getDisplayTitle = (title: string) => {
		if (!title) return 'N/A';
		if (title.length > 30) {
			return title.slice(0, 15) + '...' + title.slice(-10);
		}
		return title;
	};
</script>

{#if hasPolaProData && citation}
	<span class="polacite-wrapper">
		<button
			class="polacite-trigger"
			on:click|stopPropagation={showCitation}
			aria-label="Quelle {citation.id} anzeigen"
		>
			[{citation.id}]
		</button>
	</span>

{:else if sourceIds}
	<!-- ═══════════════════════════════════════════════════════════════
	     Standard OpenWebUI citation rendering (fallback)
	     ═══════════════════════════════════════════════════════════════ -->
	{#if (token?.ids ?? []).length == 1}
		{@const cid = token.ids[0]}
		{@const identifier = token.citationIdentifiers ? token.citationIdentifiers[0] : cid - 1}
		<Source id={identifier} title={sourceIds[cid - 1]} {onClick} />
	{:else}
		<LinkPreview.Root openDelay={0} bind:open={openPreview}>
			<LinkPreview.Trigger>
				<button
					aria-label={`${getDisplayTitle(formattedTitle(decodeString(sourceIds[token.ids[0] - 1])))} +${(token?.ids ?? []).length - 1} more sources`}
					class="text-[10px] w-fit translate-y-[2px] px-2 py-0.5 dark:bg-white/5 dark:text-white/80 dark:hover:text-white bg-gray-50 text-black/80 hover:text-black transition rounded-xl"
					on:click={() => {
						openPreview = !openPreview;
					}}
				>
					<span class="line-clamp-1">
						{getDisplayTitle(formattedTitle(decodeString(sourceIds[token.ids[0] - 1])))}
						<span class="dark:text-white/50 text-black/50">+{(token?.ids ?? []).length - 1}</span>
					</span>
				</button>
			</LinkPreview.Trigger>
			<LinkPreview.Portal>
				<LinkPreview.Content class="z-[999]" align="start" strategy="fixed" sideOffset={6}>
					<div class="bg-gray-50 dark:bg-gray-850 rounded-xl p-1 cursor-pointer">
						{#each token.citationIdentifiers ?? token.ids as identifier}
							{@const cid =
								typeof identifier === 'string' ? parseInt(identifier.split('#')[0]) : identifier}
							<div class="">
								<Source id={identifier} title={sourceIds[cid - 1]} {onClick} />
							</div>
						{/each}
					</div>
				</LinkPreview.Content>
			</LinkPreview.Portal>
		</LinkPreview.Root>
	{/if}
{:else}
	<span>{token.raw}</span>
{/if}

<style>
	/* ────────────────────────────────────────────────────────────────
	   PoLaPro Citation Popover – NotebookLM style
	   Self-contained CSS – no Tailwind dependency for the popover
	   Theme-aware: light-mode by default, dark-mode via .dark class
	   ──────────────────────────────────────────────────────────────── */

	.polacite-wrapper {
		position: relative;
		display: inline;
	}

	/* ── Trigger (inline citation link) ── */
	.polacite-trigger {
		display: inline;
		color: #2563eb;
		font-weight: 700;
		font-size: 0.75em;
		cursor: pointer;
		vertical-align: super;
		transition: color 0.15s ease;
		background: none;
		border: none;
		padding: 0 1px;
		line-height: 1;
	}
	.polacite-trigger:hover {
		color: #1d4ed8;
	}
	:global(.dark) .polacite-trigger {
		color: #3b82f6;
	}
	:global(.dark) .polacite-trigger:hover {
		color: #60a5fa;
	}

	/* ── Popover container ── */
	.polacite-popover {
		position: absolute;
		z-index: 9999;
		bottom: 100%;
		left: 0;
		margin-bottom: 0.5rem;
		width: 400px;
		max-height: 400px;
		background: #ffffff;
		border: 1px solid #e2e8f0;
		border-radius: 12px;
		box-shadow:
			0 20px 60px rgba(0, 0, 0, 0.12),
			0 0 0 1px rgba(0, 0, 0, 0.04);
		color: #374151;
		font-size: 0.875rem;
		overflow: hidden;
		transform: translateX(-10%);
		animation: polacite-fade-in 0.15s ease-out;
	}
	:global(.dark) .polacite-popover {
		background: #202123;
		border-color: #3b3b3b;
		box-shadow:
			0 20px 60px rgba(0, 0, 0, 0.45),
			0 0 0 1px rgba(255, 255, 255, 0.04);
		color: #d1d5db;
	}

	@keyframes polacite-fade-in {
		from {
			opacity: 0;
			transform: translateX(-10%) translateY(6px);
		}
		to {
			opacity: 1;
			transform: translateX(-10%) translateY(0);
		}
	}

	@keyframes polacite-fade-in-below {
		from {
			opacity: 0;
			transform: translateX(-10%) translateY(-6px);
		}
		to {
			opacity: 1;
			transform: translateX(-10%) translateY(0);
		}
	}

	/* Flipped: open below the trigger */
	.polacite-popover.polacite-below {
		bottom: auto;
		top: 100%;
		margin-bottom: 0;
		margin-top: 0.5rem;
		animation: polacite-fade-in-below 0.15s ease-out;
	}

	/* ── Header ── */
	.polacite-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 12px 16px 8px;
		border-bottom: 1px solid rgba(0, 0, 0, 0.08);
	}
	:global(.dark) .polacite-header {
		border-bottom-color: rgba(255, 255, 255, 0.08);
	}

	.polacite-header-left {
		display: flex;
		align-items: center;
		gap: 8px;
		min-width: 0;
	}

	.polacite-badge {
		background: rgba(37, 99, 235, 0.1);
		color: #2563eb;
		font-size: 0.7rem;
		font-weight: 700;
		padding: 2px 8px;
		border-radius: 6px;
		flex-shrink: 0;
	}
	:global(.dark) .polacite-badge {
		background: rgba(59, 130, 246, 0.15);
		color: #60a5fa;
	}

	.polacite-speaker {
		font-weight: 600;
		color: #1f2937;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	:global(.dark) .polacite-speaker {
		color: #e5e7eb;
	}

	.polacite-party {
		color: #6b7280;
		font-size: 0.75rem;
		flex-shrink: 0;
	}
	:global(.dark) .polacite-party {
		color: #9ca3af;
	}

	.polacite-close {
		color: #94a3b8;
		padding: 4px;
		margin-right: -4px;
		background: none;
		border: none;
		cursor: pointer;
		border-radius: 6px;
		transition: color 0.15s, background 0.15s;
	}
	.polacite-close:hover {
		color: #374151;
		background: rgba(0, 0, 0, 0.06);
	}
	:global(.dark) .polacite-close {
		color: #64748b;
	}
	:global(.dark) .polacite-close:hover {
		color: #d1d5db;
		background: rgba(255, 255, 255, 0.08);
	}

	.polacite-close-icon {
		width: 16px;
		height: 16px;
	}

	/* ── Metadata row ── */
	.polacite-meta {
		padding: 8px 16px;
		font-size: 0.72rem;
		color: #6b7280;
		display: flex;
		flex-wrap: wrap;
		gap: 4px 12px;
		border-bottom: 1px solid rgba(0, 0, 0, 0.06);
	}
	:global(.dark) .polacite-meta {
		color: #9ca3af;
		border-bottom-color: rgba(255, 255, 255, 0.06);
	}

	.polacite-score {
		color: rgba(22, 163, 74, 0.85);
	}
	:global(.dark) .polacite-score {
		color: rgba(74, 222, 128, 0.8);
	}

	/* ── Scrollable chunk text ── */
	.polacite-chunk-scroll {
		padding: 12px 16px;
		max-height: 200px;
		overflow-y: auto;
	}
	.polacite-chunk-scroll::-webkit-scrollbar {
		width: 5px;
	}
	.polacite-chunk-scroll::-webkit-scrollbar-track {
		background: transparent;
	}
	.polacite-chunk-scroll::-webkit-scrollbar-thumb {
		background: #cbd5e1;
		border-radius: 4px;
	}
	:global(.dark) .polacite-chunk-scroll::-webkit-scrollbar-thumb {
		background: #4b4b4b;
	}

	.polacite-chunk-text {
		border-left: 3px solid rgba(107, 114, 128, 0.3);
		padding-left: 12px;
		font-style: italic;
		color: #374151;
		line-height: 1.6;
		user-select: text;
		-webkit-user-select: text;
		white-space: pre-wrap;
		word-break: break-word;
	}
	:global(.dark) .polacite-chunk-text {
		border-left-color: rgba(156, 163, 175, 0.35);
		color: #d1d5db;
	}

	/* ── Footer ── */
	.polacite-footer {
		padding: 10px 16px;
		border-top: 1px solid rgba(0, 0, 0, 0.06);
		background: rgba(0, 0, 0, 0.025);
	}
	:global(.dark) .polacite-footer {
		border-top-color: rgba(255, 255, 255, 0.06);
		background: rgba(0, 0, 0, 0.15);
	}

	.polacite-link {
		color: #2563eb;
		font-size: 0.75rem;
		display: inline-flex;
		align-items: center;
		gap: 6px;
		transition: color 0.15s;
		text-decoration: none;
		width: fit-content;
	}
	.polacite-link:hover {
		color: #1d4ed8;
	}
	:global(.dark) .polacite-link {
		color: #60a5fa;
	}
	:global(.dark) .polacite-link:hover {
		color: #93bbfc;
	}

	.polacite-link-icon {
		width: 12px;
		height: 12px;
	}
</style>
