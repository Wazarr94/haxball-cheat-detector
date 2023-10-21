<script lang="ts">
	import { displayToastResult, getTime, parseDataTable } from '$lib';
	import {
		matchVal,
		type MatchMinStoreElement,
		type MatchElementMin,
		type SuspiciousAction
	} from '$lib/matchStore';
	import { compress } from 'brotli-compress';
	import { getToastStore, tableMapperValues } from '@skeletonlabs/skeleton';
	import { TabGroup, Tab } from '@skeletonlabs/skeleton';
	import { Table } from '@skeletonlabs/skeleton';
	import type { TableSource } from '@skeletonlabs/skeleton';
	import { ProgressBar } from '@skeletonlabs/skeleton';
	import Dropzone from '../components/Dropzone.svelte';
	import { handleFile } from '$lib/gameLogic';

	let matchesMinArr: MatchMinStoreElement;
	let tableSource: TableSource;

	const toastStore = getToastStore();

	let tab = 0;
	let loading = false;

	$: matchesMinArr = {
		loading: $matchVal.loading,
		error: $matchVal.error,
		matches: $matchVal.matches
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

	$: tableSource = {
		head: ['time recording', 'time match', 'player', 'pattern', 'suspicion'],
		body: tableMapperValues(parseDataTable(matchesMinArr.matches[tab]?.suspiciousActions), [
			'recTime',
			'time',
			'player',
			'pattern',
			'suspicion'
		])
	};

	async function compressJSONStringify(jsonStr: string) {
		const file = new TextEncoder().encode(jsonStr);
		const quality = 3;
		const compressed = await compress(file, {
			quality: quality
		});
		return compressed;
	}

	async function getAnalysis() {
		let suspicionsPromises = matchesMinArr.matches.map(async (match) => {
			const data = await sendMatch(match);
			return data;
		});

		loading = true;
		let error = false;

		const suspicionsRes = await Promise.allSettled(suspicionsPromises);
		const suspicions = suspicionsRes
			.map((res) => {
				if (res.status == 'fulfilled') {
					return res.value;
				} else {
					error = true;
					return { suspicions: [] };
				}
			})
			.map((res) => (error ? [] : res.suspicions));

		loading = false;
		displayToastResult(toastStore, suspicions, error);

		matchesMinArr = {
			loading: false,
			error: false,
			matches: [
				...matchesMinArr.matches.map((match, index) => {
					return {
						...match,
						suspiciousActions: suspicions[index]
					} satisfies MatchElementMin;
				})
			]
		} satisfies MatchMinStoreElement;
	}

	async function sendMatch(match: MatchElementMin): Promise<{ suspicions: SuspiciousAction[] }> {
		let sendFile = JSON.stringify(match);
		const compressedFile = await compressJSONStringify(sendFile);

		const url =
			process.env.NODE_ENV == 'development'
				? 'http://localhost:8000/recording'
				: 'https://haxball-cheat-detector-production.up.railway.app/recording';

		const res = await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Content-Encoding': 'br'
			},
			body: compressedFile
		});
		return res.json();
	}
</script>

<h1 class="text-center h1 p-8">Haxball Cheat Detector</h1>

<div class="flex flex-row text-center justify-center text-l pb-8 gap-4">
	<p class="w-1/3">
		This website is a tool to detect cheaters in Haxball on any map. We catch macro abusers by
		looking at streaks of very fast inputs.<br /> <br />We hope to adapt this tool for other
		cheating patterns in the future.
	</p>
</div>

<Dropzone
	on:newFile={() => {
		tab = 0;
	}}
	on:processFile={getAnalysis}
/>

{#if loading}
	<ProgressBar value={undefined} />
{/if}

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
						<h3 class="h3">Score: {match.scoreRed} - {match.scoreBlue}</h3>
						<h3 class="h3">Game time: {getTime(match.gameTicks)}</h3>
						{#if match.suspiciousActions && match.suspiciousActions.length > 0}
							<h2 class="h2 pt-2">Suspicious actions:</h2>
							<Table class="p-4" source={tableSource} />
						{/if}
					</div>
				{/if}
			{/each}
		</svelte:fragment>
	</TabGroup>
{/if}
