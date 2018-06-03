import { Pipe, PipeTransform } from '@angular/core';
import { formatDate } from '@angular/common';

@Pipe({
    name: 'period'
})
export class PeriodPipe implements PipeTransform {

    transform(value: string, period: string): any {
        switch (period) {
        case 'weekly':
            const [year, week] = value.split('-');
            return `Week ${week} of ${year}`;
        case 'monthly':
            value = `${value}-01`;
            return formatDate(value, 'MMMM y', 'en-GB');
        case 'yearly':
        default:
            return value;
        }
    }

}
