interface EmptyStateProps {
  title: string;
  detail?: string;
}

export function EmptyState({ title, detail }: EmptyStateProps) {
  return (
    <div className="rounded-md border border-dashed border-court-line bg-white px-5 py-8 text-sm">
      <p className="font-medium text-court-ink">{title}</p>
      {detail ? <p className="mt-1 text-court-muted">{detail}</p> : null}
    </div>
  );
}
