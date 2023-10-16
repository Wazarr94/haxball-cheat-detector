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
	return 'TODO';
	// return `${minutesStr}:${secondsStr}`;
}
