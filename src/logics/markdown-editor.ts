import type { ToolbarNames } from 'md-editor-v3'

export const fullMarkdownToolbars: ToolbarNames[] = [
  'bold',
  'underline',
  'italic',
  '-',
  'title',
  'strikeThrough',
  'sub',
  'sup',
  'quote',
  'unorderedList',
  'orderedList',
  'task',
  '-',
  'codeRow',
  'code',
  'link',
  'image',
  'table',
  'mermaid',
  'katex',
  '-',
  'revoke',
  'next',
  '=',
  'preview',
  'previewOnly',
  'fullscreen',
  'htmlPreview',
  'catalog',
]

export const compactMarkdownToolbars: ToolbarNames[] = [
  'bold',
  'italic',
  'quote',
  'unorderedList',
  'orderedList',
  'code',
  'link',
  'image',
  '-',
  'revoke',
  'next',
  '=',
  'preview',
  'previewOnly',
]

export function buildSummaryFromMarkdown(content: string, max = 100) {
  const plain = content
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[[^\]]+\]\([^)]*\)/g, '$1')
    .replace(/[`*_>#-]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
  if (!plain)
    return ''
  return plain.length > max ? `${plain.slice(0, max)}...` : plain
}

