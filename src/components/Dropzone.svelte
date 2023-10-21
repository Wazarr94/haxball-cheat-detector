<script lang="ts">
	import { handleFile } from '$lib/gameLogic';
	import { FileDropzone } from '@skeletonlabs/skeleton';
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();
	let fileList: FileList;

	type DropzoneMessage = {
		message: string;
		meta: string;
	};

	let messageNormal = {
		message: `<p class="font-bold">Upload the recording here !</p>`,
		meta: `<p class="text-sm opacity-75">HBR2 files only</p>`
	} as DropzoneMessage;

	let messageDrag = {
		message: `<p class="font-bold">Drop here !</p>`,
		meta: ``
	};

	let messageUpload = messageNormal;

	let handleDragEnter: (e: DragEvent) => void = (e) => {
		messageUpload = messageDrag;
	};

	let handleDragLeave: (e: DragEvent) => void = (e) => {
		messageUpload = messageNormal;
	};

	let handleFileSvelte: (e: Event) => void = (e) => {
		dispatch('newFile', e);
		handleFile(e);
	};
</script>

<div class="flex flex-row justify-center items-center gap-4 pb-8">
	<div class="flex-col w-2/3">
		<FileDropzone
			name="file"
			multiple="multiple"
			accept=".hbr2"
			bind:files={fileList}
			on:change={handleFileSvelte}
			on:dragenter={handleDragEnter}
			on:dragleave={handleDragLeave}
			on:drop={handleDragLeave}
		>
			<svelte:fragment slot="message">
				{@html messageUpload.message}
				<div class="opacity-75">
					{@html messageUpload.meta}
				</div>
			</svelte:fragment>
		</FileDropzone>
		{#if fileList}
			{#if fileList.length == 1}
				<div class="flex flex-row justify-center pt-2">
					<p class="text-sm opacity-75">File: {fileList[0].name}</p>
				</div>
			{:else}
				<div class="flex flex-row justify-center pt-2">
					<p class="text-sm opacity-75">{fileList.length} files uploaded</p>
				</div>
			{/if}
		{/if}
	</div>
	<button
		class="p-2 btn variant-ghost-tertiary"
		on:click={(e) => dispatch('processFile', e)}
		disabled={fileList && fileList.length == 0}>Get suspicious runs</button
	>
</div>
