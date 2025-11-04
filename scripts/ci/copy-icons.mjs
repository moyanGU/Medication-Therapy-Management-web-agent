// Cross-platform copy of PWA icons from public/icons to dist/icons
// Ensures /icons/* exists in the production bundle even if plugin copying is skipped
import { cp, mkdir, access } from 'fs/promises'
import path from 'path'

async function main() {
  const projectRoot = process.cwd()
  const srcDir = path.resolve(projectRoot, 'public', 'icons')
  const destDir = path.resolve(projectRoot, 'dist', 'icons')

  try {
    await access(srcDir)
  } catch {
    console.log('[postbuild] No public/icons directory found, skipping copy.')
    return
  }

  await mkdir(destDir, { recursive: true })

  try {
    await cp(srcDir, destDir, { recursive: true })
    console.log(`[postbuild] Copied icons from ${srcDir} to ${destDir}`)
  } catch (err) {
    console.error('[postbuild] Failed to copy icons:', err)
    process.exit(1)
  }
}

main()