import React from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import { CustomYoutube } from './extensions/CustomYoutube';
import TextAlign from '@tiptap/extension-text-align';

import { CustomTable } from './extensions/CustomTable';
import { CustomImage } from './extensions/CustomImage';
import { NoteLink } from './extensions/NoteLink';

import { EditorToolbar } from './EditorToolbar';
import './Editor.css';

interface LifeOSEditorProps {
  content: string;
  onChange?: (html: string) => void;
}

export const LifeOSEditor: React.FC<LifeOSEditorProps> = ({ content, onChange }) => {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        link: { // Konfiguracja linku wewnątrz StarterKit
          openOnClick: false,
          HTMLAttributes: { class: 'my-link-class' },
        }
      }),
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      CustomTable.configure({
        resizable: true,
      }),
      TableRow,
      TableHeader,
      TableCell,
      CustomImage,
      CustomYoutube.configure({
        inline: false,
      }),
      NoteLink,
    ],
    content,
    onUpdate: ({ editor }) => {
      onChange?.(editor.getHTML());
    },
    editorProps: {
      attributes: {
        class: 'prose prose-invert max-w-none text-slate-200 focus:outline-none min-h-full h-full p-6 pb-64',
      },
      handleDrop: (view, event, _slice, moved) => {
        if (!moved && event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files[0]) {
          const file = event.dataTransfer.files[0];
          if (file.type.startsWith('image/')) {
            event.preventDefault();
            // TODO: w przyszłości podpięcie pod upload na S3/backend. Na teraz wstawiamy data-url
            const reader = new FileReader();
            reader.onload = (e) => {
              const src = e.target?.result as string;
              const { schema } = view.state;
              const coordinates = view.posAtCoords({ left: event.clientX, top: event.clientY });
              const node = schema.nodes.image.create({ src });
              const transaction = view.state.tr.insert(coordinates?.pos || 0, node);
              view.dispatch(transaction);
            };
            reader.readAsDataURL(file);
            return true;
          }
        }
        return false;
      },
    },
  });

  if (!editor) return null;

  return (
    <div className="border border-slate-800 rounded-lg bg-slate-950 shadow-sm flex flex-col w-full h-full tiptap-wrapper">
      <EditorToolbar editor={editor} />
      <div className="flex-1 overflow-y-auto cursor-text tiptap" onClick={() => editor.commands.focus()}>
        <EditorContent editor={editor} className="h-full" />
      </div>
    </div>
  );
};