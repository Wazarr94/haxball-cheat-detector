<script lang="ts">
	import { getTime } from '$lib';
	import { handleFile } from '$lib/gameLogic';
	import {
		matchStore,
		type MatchMinStoreElement,
		type MatchStoreElement,
		type MatchElementMin,
		type SuspiciousAction
	} from '$lib/matchStore';
	import { FileDropzone, tableMapperValues } from '@skeletonlabs/skeleton';
	import { TabGroup, Tab } from '@skeletonlabs/skeleton';
	import { Table } from '@skeletonlabs/skeleton';
	import type { TableSource } from '@skeletonlabs/skeleton';

	let matchesArr: MatchStoreElement;
	let matchesMinArr: MatchMinStoreElement;

	matchStore.subscribe((value) => {
		matchesArr = value;
	});

	$: matchesMinArr = {
		loading: matchesArr.loading,
		error: matchesArr.error,
		matches: matchesArr.matches
			.filter((match) => match.gameTicks > 1)
			.map((match) => {
				return {
					scoreRed: match.scoreRed,
					scoreBlue: match.scoreBlue,
					gameTicks: match.gameTicks,
					playerActions: match.playerActions,
					suspiciousActions: []
				} satisfies MatchElementMin;
			})
	};

	async function getAnalysis() {
		let sendFile = JSON.stringify(matchesMinArr);
		let sizeOctetSendFile = new TextEncoder().encode(sendFile).length;
		let sizeMB = Math.round((sizeOctetSendFile / 1000000) * 100) / 100;
		console.log(`Size of file: ${sizeMB} MB`);

		const res = await fetch('api/recording', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(matchesMinArr)
		});
		const data = await res.json();
		console.log(data);
		let value = matchesMinArr.matches.map((match, index) => {
			return {
				...match,
				suspiciousActions: data.matches[index]
			} satisfies MatchElementMin;
		});
		matchesMinArr = {
			loading: false,
			error: false,
			matches: value
		} satisfies MatchMinStoreElement;
	}

	let tab = 0;
	let suspiciousActions: SuspiciousAction[] | undefined;
	$: suspiciousActions = matchesMinArr.matches[tab]?.suspiciousActions;
	const tableSource: TableSource = {
		head: ['frame', 'player', 'pattern', 'suspicion'],
		body: tableMapperValues(suspiciousActions || [], ['frame', 'player', 'pattern', 'suspicion'])
	};
</script>

<h1 class="text-center h1 p-8">Haxball Cheat Detector</h1>
<div class="flex flex-row justify-center items-center gap-4 pb-8">
	<FileDropzone name="file" accept=".hbr2" class="w-2/3" on:change={handleFile}>
		<svelte:fragment slot="message">
			<p class="font-bold">Upload the recording here !</p>
			<p class="text-sm">Only .hbr2 files are accepted</p>
		</svelte:fragment>
	</FileDropzone>
	<button
		class="p-2 btn variant-ghost-tertiary"
		on:click={getAnalysis}
		disabled={matchesMinArr.matches.length == 0}>Get suspicious runs</button
	>
</div>

{#if matchesMinArr.loading}
	<p>Loading...</p>
{:else if matchesMinArr.error}
	<p>Bad file</p>
{:else if matchesMinArr.matches.length > 0}
	<TabGroup>
		{#each matchesMinArr.matches as match, index}
			<Tab bind:group={tab} value={index} name={`Match ${index}`}>
				Match {index + 1} ({match.suspiciousActions?.length})
			</Tab>
		{/each}
		<svelte:fragment slot="panel">
			{#each matchesMinArr.matches as match, index}
				{#if tab == index}
					<div class="p-4">
						<h3 class="h3">Match {index + 1}: {match.scoreRed} - {match.scoreBlue}</h3>
						{#if match.suspiciousActions}
							<p>Suspicious actions: {match.suspiciousActions.length}</p>
							{#if match.suspiciousActions.length > 0}
								<Table source={tableSource} />
							{/if}
						{/if}
					</div>
				{/if}
			{/each}
		</svelte:fragment>
	</TabGroup>
{/if}
