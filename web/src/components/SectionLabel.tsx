type SectionLabelProps = {
  index: string;
  children: React.ReactNode;
};

export function SectionLabel({ index, children }: SectionLabelProps) {
  return (
    <div className="section-label">
      <span>{index}</span>
      <p>{children}</p>
    </div>
  );
}
