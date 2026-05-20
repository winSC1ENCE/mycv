import { useI18n } from "vue-i18n";

export function useLevelLabel(): (level: number) => string {
  const { t } = useI18n();
  return (level: number): string => {
    const clamped = Math.min(5, Math.max(1, Math.round(level)));
    return t(`skills.levels.${clamped}`);
  };
}
