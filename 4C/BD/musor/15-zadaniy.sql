-- 1. Вывести абитуриентов, которые хотят поступать на определенную образовательную программу.
SELECT e.name_enrollee
FROM enrollee e
JOIN program_enrollee pe ON e.enrollee_id = pe.enrollee_id
JOIN program p ON pe.program_id = p.program_id
WHERE p.name_program = 'Дизайн';

-- 2. Вывести образовательные программы, на которые для поступления необходим определенный предмет ЕГЭ.
SELECT p.name_program
FROM program p
JOIN program_subject ps ON p.program_id = ps.program_id
JOIN subject s ON ps.subject_id = s.subject_id
WHERE s.name_subject = 'Русский Язык';

-- 3. Вывести статистическую информацию по каждому предмету ЕГЭ (минимальный и максимальный балл, количество абитуриентов, которые этот предмет сдавали).
SELECT 
    s.name_subject,
    MIN(es.result) AS min_score,
    MAX(es.result) AS max_score,
    COUNT(es.enrollee_id) AS applicants_count
FROM subject s
JOIN enrollee_subject es ON s.subject_id = es.subject_id
GROUP BY s.subject_id, s.name_subject;

-- 4. Вывести образовательные программы, минимальные баллы по каждому предмету которых, превышают заданное значение.
SELECT p.name_program
FROM program p
JOIN program_subject ps ON p.program_id = ps.program_id
GROUP BY p.program_id, p.name_program
HAVING MIN(ps.min_result) > 50;

-- 5. Вывести образовательные программы, которые имеют самый большой план набора.
SELECT name_program, plan
FROM program
WHERE plan = (SELECT MAX(plan) FROM program);

-- 6. Посчитать, сколько дополнительных баллов получит каждый абитуриент.
SELECT 
    e.name_enrollee,
    COALESCE(SUM(a.bonus), 0) AS total_bonus
FROM enrollee e
LEFT JOIN enrollee_achievement ea ON e.enrollee_id = ea.enrollee_id
LEFT JOIN achievement a ON ea.achievement_id = a.achievement_id
GROUP BY e.enrollee_id, e.name_enrollee;

-- 7. Посчитать конкурс на каждую образовательную программу.
SELECT 
    p.name_program,
    COUNT(pe.enrollee_id) AS applicants_count,
    p.plan AS admission_plan,
    COUNT(pe.enrollee_id)::DECIMAL / p.plan AS competition
FROM program p
JOIN program_enrollee pe ON p.program_id = pe.program_id
GROUP BY p.program_id, p.name_program, p.plan;

-- 8. Вывести образовательные программы, на которые для поступления необходимы два определенных предмета ЕГЭ.
SELECT p.name_program
FROM program p
JOIN program_subject ps ON p.program_id = ps.program_id
JOIN subject s ON ps.subject_id = s.subject_id
WHERE s.name_subject IN ('Предмет1', 'Предмет2')
GROUP BY p.program_id, p.name_program
HAVING COUNT(DISTINCT s.subject_id) = 2;

-- 9. Посчитать количество баллов каждого абитуриента на каждую образовательную программу по результатам ЕГЭ.
SELECT 
    e.name_enrollee,
    p.name_program,
    SUM(es.result) AS total_score
FROM enrollee e
JOIN program_enrollee pe ON e.enrollee_id = pe.enrollee_id
JOIN program p ON pe.program_id = p.program_id
JOIN program_subject ps ON p.program_id = ps.program_id
JOIN enrollee_subject es ON e.enrollee_id = es.enrollee_id AND ps.subject_id = es.subject_id
GROUP BY e.enrollee_id, e.name_enrollee, p.program_id, p.name_program;

-- 10. Вывести абитуриентов, которые не могут быть зачислены на образовательную программу.
SELECT DISTINCT e.name_enrollee, p.name_program
FROM enrollee e
JOIN program_enrollee pe ON e.enrollee_id = pe.enrollee_id
JOIN program p ON pe.program_id = p.program_id
JOIN program_subject ps ON p.program_id = ps.program_id
LEFT JOIN enrollee_subject es ON e.enrollee_id = es.enrollee_id AND ps.subject_id = es.subject_id
WHERE es.result IS NULL OR es.result < ps.min_result;

-- 11. Создается таблица с суммой баллов абитуриентов по предметам ЕГЭ в соответствии с поданными заявлениями.
CREATE TABLE applicant_total_scores AS
SELECT 
    e.enrollee_id,
    e.name_enrollee,
    p.program_id,
    p.name_program,
    SUM(es.result) + COALESCE((
        SELECT SUM(a.bonus)
        FROM enrollee_achievement ea
        JOIN achievement a ON ea.achievement_id = a.achievement_id
        WHERE ea.enrollee_id = e.enrollee_id
    ), 0) AS total_score
FROM enrollee e
JOIN program_enrollee pe ON e.enrollee_id = pe.enrollee_id
JOIN program p ON pe.program_id = p.program_id
JOIN program_subject ps ON p.program_id = ps.program_id
JOIN enrollee_subject es ON e.enrollee_id = es.enrollee_id AND ps.subject_id = es.subject_id
GROUP BY e.enrollee_id, e.name_enrollee, p.program_id, p.name_program;

-- 12. Из таблицы удаляются абитуриенты, если они не набрали минимального балла по предмету, необходимому для поступления на образовательную программу.
DELETE FROM applicant_total_scores ats
WHERE EXISTS (
    SELECT 1
    FROM program_subject ps
    JOIN enrollee_subject es ON ps.subject_id = es.subject_id
    WHERE ps.program_id = ats.program_id
    AND es.enrollee_id = ats.enrollee_id
    AND es.result < ps.min_result
);

-- 13. Абитуриентам, у которых есть медаль или значок ГТО, добавляются дополнительные баллы.
UPDATE applicant_total_scores
SET total_score = total_score + COALESCE((
    SELECT SUM(a.bonus)
    FROM enrollee_achievement ea
    JOIN achievement a ON ea.achievement_id = a.achievement_id
    WHERE ea.enrollee_id = applicant_total_scores.enrollee_id
    AND a.name_achievement IN ('Золотая медаль', 'Значок ГТО')
), 0);

-- 14. Абитуриенты сортируются в соответствии с набранными баллами по каждой образовательной программе.
SELECT 
    name_program,
    name_enrollee,
    total_score
FROM applicant_total_scores
ORDER BY program_id, total_score DESC;

-- 15. Формируется список абитуриентов, рекомендованных к зачислению с указанием суммы баллов (вставляется столбец для нумерации, осуществляется нумерация студентов по образовательной программе, выбираются абитуриенты с наибольшими баллами в соответствии с планом набора). Для каждого студента определяется разница между его суммой баллов и суммой баллов предыдущего абитуриента.
WITH ranked_applicants AS (
    SELECT 
        ats.enrollee_id,
        ats.name_enrollee,
        ats.program_id,
        ats.name_program,
        ats.total_score,
        p.plan,
        ROW_NUMBER() OVER (PARTITION BY ats.program_id ORDER BY ats.total_score DESC) AS rank_num,
        LAG(ats.total_score) OVER (PARTITION BY ats.program_id ORDER BY ats.total_score DESC) AS prev_score
    FROM applicant_total_scores ats
    JOIN program p ON ats.program_id = p.program_id
)
SELECT 
    rank_num AS admission_number,
    name_enrollee,
    name_program,
    total_score,
    CASE 
        WHEN prev_score IS NULL THEN NULL
        ELSE total_score - prev_score
    END AS score_difference
FROM ranked_applicants
WHERE rank_num <= plan
ORDER BY program_id, rank_num;