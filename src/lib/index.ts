import type { ToastSettings, ToastStore } from '@skeletonlabs/skeleton';
import type { SuspiciousAction } from './matchStore';

// place files you want to import through the `$lib` alias in this folder.
export function getTime(frames: number) {
	const timeSeconds = Math.floor(frames / 60);
	const minutes = Math.floor(timeSeconds / 60);
	const seconds = timeSeconds % 60;
	const minutesStr = `${minutes < 10 ? '0' : ''}${minutes}`;
	const secondsStr = `${seconds < 10 ? '0' : ''}${seconds}`;
	return `${minutesStr}:${secondsStr}`;
}

export function getTimeMs(timeMs: number) {
	const timeSeconds = Math.floor(timeMs / 1000);
	const minutes = Math.floor(timeSeconds / 60);
	const seconds = timeSeconds % 60;
	const minutesStr = `${minutes < 10 ? '0' : ''}${minutes}`;
	const secondsStr = `${seconds < 10 ? '0' : ''}${seconds}`;
	return `${minutesStr}:${secondsStr}`;
}

export function displayToastResult(
	toastStore: ToastStore,
	suspicions: SuspiciousAction[][],
	err: boolean
) {
	if (err) {
		const toast: ToastSettings = {
			message: 'API error, please try again',
			background: 'variant-filled-primary',
			timeout: 3000,
			hideDismiss: true
		};
		toastStore.trigger(toast);
		return;
	}

	const suspicionsTotal = suspicions.reduce((acc, curr) => {
		return acc + curr.length;
	}, 0);
	const toast: ToastSettings = {
		message: `${suspicionsTotal} suspicious actions found`,
		background: 'variant-filled-secondary',
		hideDismiss: true,
		timeout: 3000
	};
	toastStore.trigger(toast);
}

export function parseDataTable(data: SuspiciousAction[] | undefined) {
	return (data || []).map((action) => {
		return {
			recTime: getTimeMs(action.recMs),
			time: getTime(action.frame),
			player: action.player,
			pattern: `${action.pattern.change_frame} frame actions for ${action.pattern.consecutive_frames} frames`,
			suspicion: action.pattern.suspicion
		};
	});
}
