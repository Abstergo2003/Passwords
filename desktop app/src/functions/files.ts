import { readFile, mkdir, BaseDirectory } from '@tauri-apps/plugin-fs';

async function readFileAsBase64(filePath: string): Promise<string> {
    try {
        // Read file as Uint8Array
        const contents = await readFile(filePath, {baseDir: BaseDirectory.AppLocalData});
        // Convert Uint8Array to base64
        const base64 = btoa(
        Array.from(contents)
            .map(byte => String.fromCharCode(byte))
            .join('')
        );
        
        return base64;
    } catch (error) {
        console.error('Error reading file:', error);
        throw error;
    }
}

async function newFolder(path:string) {
    await mkdir(path, {baseDir: BaseDirectory.AppLocalData, recursive: true})
}

export {readFileAsBase64, newFolder}